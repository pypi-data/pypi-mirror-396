import copy
import os
import re
import shutil
from pathlib import Path
from typing import Optional

import click
import yaml

import dbt.config
import dbt_common.clients.system
from dbt.adapters.factory import get_include_paths, load_plugin
from dbt.config.profile import read_profile
from dbt.contracts.util import Identifier as ProjectName
from dbt.events.types import (
    ConfigFolderDirectory,
    InvalidProfileTemplateYAML,
    NoSampleProfileFound,
    ProfileWrittenWithProjectTemplateYAML,
    ProfileWrittenWithSample,
    ProfileWrittenWithTargetTemplateYAML,
    ProjectCreated,
    ProjectNameAlreadyExists,
    SettingUpProfile,
    StarterProjectPath,
)
from dbt.flags import get_flags
from dbt.task.base import BaseTask, move_to_nearest_project_dir
from dbt.version import _get_adapter_plugin_names
from dbt_common.events.functions import fire_event
from dbt_common.exceptions import DbtRuntimeError

DOCS_URL = "https://docs.getdbt.com/docs/configure-your-profile"
SLACK_URL = "https://community.getdbt.com/"

# This file is not needed for the starter project but exists for finding the resource path
IGNORE_FILES = ["__init__.py", "__pycache__"]


# https://click.palletsprojects.com/en/8.0.x/api/#types
# click v7.0 has UNPROCESSED, STRING, INT, FLOAT, BOOL, and UUID available.
click_type_mapping = {
    "string": click.STRING,
    "int": click.INT,
    "float": click.FLOAT,
    "bool": click.BOOL,
    None: None,
}


class InitTask(BaseTask):
    def copy_starter_repo(self, project_name: str) -> None:
        # Lazy import to avoid ModuleNotFoundError
        from dbt.include.starter_project import (
            PACKAGE_PATH as starter_project_directory,
        )

        fire_event(StarterProjectPath(dir=starter_project_directory))
        shutil.copytree(
            starter_project_directory, project_name, ignore=shutil.ignore_patterns(*IGNORE_FILES)
        )

    def create_profiles_dir(self, profiles_dir: str) -> bool:
        """Create the user's profiles directory if it doesn't already exist."""
        profiles_path = Path(profiles_dir)
        if not profiles_path.exists():
            fire_event(ConfigFolderDirectory(dir=str(profiles_dir)))
            dbt_common.clients.system.make_directory(profiles_dir)
            return True
        return False

    def create_profile_from_sample(self, adapter: str, profile_name: str):
        """Create a profile entry using the adapter's sample_profiles.yml

        Renames the profile in sample_profiles.yml to match that of the project."""
        # Line below raises an exception if the specified adapter is not found
        load_plugin(adapter)
        adapter_path = get_include_paths(adapter)[0]
        sample_profiles_path = adapter_path / "sample_profiles.yml"

        if not sample_profiles_path.exists():
            fire_event(NoSampleProfileFound(adapter=adapter))
        else:
            with open(sample_profiles_path, "r") as f:
                sample_profile = f.read()
            sample_profile_name = list(yaml.safe_load(sample_profile).keys())[0]
            # Use a regex to replace the name of the sample_profile with
            # that of the project without losing any comments from the sample
            sample_profile = re.sub(f"^{sample_profile_name}:", f"{profile_name}:", sample_profile)
            profiles_filepath = Path(get_flags().PROFILES_DIR) / Path("profiles.yml")
            if profiles_filepath.exists():
                with open(profiles_filepath, "a") as f:
                    f.write("\n" + sample_profile)
            else:
                with open(profiles_filepath, "w") as f:
                    f.write(sample_profile)
                fire_event(
                    ProfileWrittenWithSample(name=profile_name, path=str(profiles_filepath))
                )

    def generate_target_from_input(self, profile_template: dict, target: dict = {}) -> dict:
        """Generate a target configuration from profile_template and user input."""
        profile_template_local = copy.deepcopy(profile_template)
        for key, value in profile_template_local.items():
            if key.startswith("_choose"):
                choice_type = key[8:].replace("_", " ")
                option_list = list(value.keys())
                prompt_msg = (
                    "\n".join([f"[{n + 1}] {v}" for n, v in enumerate(option_list)])
                    + f"\nDesired {choice_type} option (enter a number)"
                )
                numeric_choice = click.prompt(prompt_msg, type=click.INT)
                choice = option_list[numeric_choice - 1]
                # Complete the chosen option's values in a recursive call
                target = self.generate_target_from_input(
                    profile_template_local[key][choice], target
                )
            else:
                if key.startswith("_fixed"):
                    # _fixed prefixed keys are not presented to the user
                    target[key[7:]] = value
                else:
                    hide_input = value.get("hide_input", False)
                    default = value.get("default", None)
                    hint = value.get("hint", None)
                    type = click_type_mapping[value.get("type", None)]
                    text = key + (f" ({hint})" if hint else "")
                    target[key] = click.prompt(
                        text, default=default, hide_input=hide_input, type=type
                    )
        return target

    def get_profile_name_from_current_project(self) -> str:
        """Reads dbt_project.yml in the current directory to retrieve the
        profile name.
        """
        with open("dbt_project.yml") as f:
            dbt_project = yaml.safe_load(f)
        return dbt_project["profile"]

    def write_profile(self, profile: dict, profile_name: str):
        """Given a profile, write it to the current project's profiles.yml.
        This will overwrite any profile with a matching name."""
        # Create the profile directory if it doesn't exist
        profiles_filepath = Path(get_flags().PROFILES_DIR) / Path("profiles.yml")

        profiles = {profile_name: profile}

        if profiles_filepath.exists():
            with open(profiles_filepath, "r") as f:
                profiles = yaml.safe_load(f) or {}
                profiles[profile_name] = profile

        # Write the profiles dictionary to a brand-new or pre-existing file
        with open(profiles_filepath, "w") as f:
            yaml.dump(profiles, f)

    def create_profile_from_profile_template(self, profile_template: dict, profile_name: str):
        """Create and write a profile using the supplied profile_template."""
        initial_target = profile_template.get("fixed", {})
        prompts = profile_template.get("prompts", {})
        target = self.generate_target_from_input(prompts, initial_target)
        target_name = target.pop("target", "dev")
        profile = {"outputs": {target_name: target}, "target": target_name}
        self.write_profile(profile, profile_name)

    def create_profile_from_target(self, adapter: str, profile_name: str):
        """Create a profile without defaults using target's profile_template.yml if available, or
        sample_profiles.yml as a fallback."""
        # Line below raises an exception if the specified adapter is not found
        load_plugin(adapter)
        adapter_path = get_include_paths(adapter)[0]
        profile_template_path = adapter_path / "profile_template.yml"

        if profile_template_path.exists():
            with open(profile_template_path) as f:
                profile_template = yaml.safe_load(f)
            self.create_profile_from_profile_template(profile_template, profile_name)
            profiles_filepath = Path(get_flags().PROFILES_DIR) / Path("profiles.yml")
            fire_event(
                ProfileWrittenWithTargetTemplateYAML(
                    name=profile_name, path=str(profiles_filepath)
                )
            )
        else:
            # For adapters without a profile_template.yml defined, fallback on
            # sample_profiles.yml
            self.create_profile_from_sample(adapter, profile_name)

    def check_if_profile_exists(self, profile_name: str) -> bool:
        """
        Validate that the specified profile exists. Can't use the regular profile validation
        routine because it assumes the project file exists
        """
        profiles_dir = get_flags().PROFILES_DIR
        raw_profiles = read_profile(profiles_dir)
        return profile_name in raw_profiles

    def check_if_can_write_profile(self, profile_name: Optional[str] = None) -> bool:
        """Using either a provided profile name or that specified in dbt_project.yml,
        check if the profile already exists in profiles.yml, and if so ask the
        user whether to proceed and overwrite it."""
        profiles_file = Path(get_flags().PROFILES_DIR) / Path("profiles.yml")
        if not profiles_file.exists():
            return True
        profile_name = profile_name or self.get_profile_name_from_current_project()
        with open(profiles_file, "r") as f:
            profiles = yaml.safe_load(f) or {}
        if profile_name in profiles.keys():
            # Profile already exists, just skip profile setup
            click.echo(f"Profile '{profile_name}' already exists in {profiles_file}, skipping profile setup.")
            return False
        else:
            return True

    def create_profile_using_project_profile_template(self, profile_name):
        """Create a profile using the project's profile_template.yml"""
        with open("profile_template.yml") as f:
            profile_template = yaml.safe_load(f)
        self.create_profile_from_profile_template(profile_template, profile_name)
        profiles_filepath = Path(get_flags().PROFILES_DIR) / Path("profiles.yml")
        fire_event(
            ProfileWrittenWithProjectTemplateYAML(name=profile_name, path=str(profiles_filepath))
        )

    def ask_for_adapter_choice(self) -> str:
        """Ask the user which adapter (database) they'd like to use."""
        available_adapters = list(_get_adapter_plugin_names())

        if not available_adapters:
            raise dbt.exceptions.NoAdaptersAvailableError()

        prompt_msg = (
            "Which database would you like to use?\n"
            + "\n".join([f"[{n + 1}] {v}" for n, v in enumerate(available_adapters)])
            + "\n\n(Don't see the one you want? https://docs.getdbt.com/docs/available-adapters)"
            + "\n\nEnter a number"
        )
        numeric_choice = click.prompt(prompt_msg, type=click.INT)
        return available_adapters[numeric_choice - 1]

    def setup_profile(self, profile_name: str) -> None:
        """Set up a new profile for a project"""
        fire_event(SettingUpProfile())
        if not self.check_if_can_write_profile(profile_name=profile_name):
            return
        # If a profile_template.yml exists in the project root, that effectively
        # overrides the profile_template.yml for the given target.
        profile_template_path = Path("profile_template.yml")
        if profile_template_path.exists():
            try:
                # This relies on a valid profile_template.yml from the user,
                # so use a try: except to fall back to the default on failure
                self.create_profile_using_project_profile_template(profile_name)
                return
            except Exception:
                fire_event(InvalidProfileTemplateYAML())
        adapter = self.ask_for_adapter_choice()
        self.create_profile_from_target(adapter, profile_name=profile_name)

    def get_adapter_metadata(self) -> dict:
        """Get categorized adapter information with descriptions - COMPREHENSIVE."""
        return {
            "Cloud Data Warehouses": {
                "snowflake": {"name": "Snowflake", "desc": "Cloud data warehouse", "jdbc": True},
                "bigquery": {"name": "Google BigQuery", "desc": "Serverless warehouse", "jdbc": True},
                "databricks": {"name": "Databricks", "desc": "Lakehouse platform", "jdbc": True},
                "redshift": {"name": "Amazon Redshift", "desc": "AWS warehouse", "jdbc": True},
                "firebolt": {"name": "Firebolt", "desc": "Cloud DW for analytics", "jdbc": True},
            },
            "Microsoft Ecosystem": {
                "fabric": {"name": "Microsoft Fabric", "desc": "Unified analytics", "jdbc": True},
                "synapse": {"name": "Azure Synapse", "desc": "Analytics service", "jdbc": True},
                "sqlserver": {"name": "SQL Server", "desc": "Enterprise RDBMS", "jdbc": True},
            },
            "Enterprise Data Warehouses": {
                "teradata": {"name": "Teradata", "desc": "Enterprise warehouse", "jdbc": True},
                "oracle": {"name": "Oracle Database", "desc": "Enterprise RDBMS", "jdbc": True},
                "db2": {"name": "IBM DB2", "desc": "IBM database system", "jdbc": True},
                "exasol": {"name": "Exasol", "desc": "In-memory analytics", "jdbc": True},
                "vertica": {"name": "Vertica", "desc": "Columnar analytics", "jdbc": True},
            },
            "SQL Engines & Query Platforms": {
                "spark": {"name": "Apache Spark", "desc": "Unified analytics", "jdbc": True},
                "trino": {"name": "Trino", "desc": "Distributed SQL engine", "jdbc": True},
                "presto": {"name": "Presto", "desc": "Meta's query engine", "jdbc": True},
                "athena": {"name": "Amazon Athena", "desc": "Query S3 data", "jdbc": True},
                "dremio": {"name": "Dremio", "desc": "Data lakehouse platform", "jdbc": True},
                "hive": {"name": "Apache Hive", "desc": "Hadoop data warehouse", "jdbc": True},
                "impala": {"name": "Cloudera Impala", "desc": "MPP SQL engine", "jdbc": True},
                "glue": {"name": "AWS Glue", "desc": "Serverless ETL", "jdbc": True},
            },
            "Open Source Databases": {
                "postgres": {"name": "PostgreSQL", "desc": "Popular open-source DB", "jdbc": True},
                "mysql": {"name": "MySQL", "desc": "World's most popular DB", "jdbc": True},
                "mariadb": {"name": "MariaDB", "desc": "MySQL fork", "jdbc": True},
                "sqlite": {"name": "SQLite", "desc": "Embedded database", "jdbc": False},
                "duckdb": {"name": "DuckDB", "desc": "In-process OLAP", "jdbc": False},
                "cratedb": {"name": "CrateDB", "desc": "Distributed SQL", "jdbc": True},
            },
            "OLAP & Analytics Databases": {
                "clickhouse": {"name": "ClickHouse", "desc": "Fast OLAP database", "jdbc": True},
                "starrocks": {"name": "StarRocks", "desc": "MPP analytics", "jdbc": True},
                "doris": {"name": "Apache Doris", "desc": "Real-time analytics", "jdbc": True},
                "greenplum": {"name": "Greenplum", "desc": "MPP database", "jdbc": True},
                "monetdb": {"name": "MonetDB", "desc": "Columnar database", "jdbc": True},
            },
            "Time-Series & Streaming": {
                "timescaledb": {"name": "TimescaleDB", "desc": "PostgreSQL for time-series", "jdbc": True},
                "questdb": {"name": "QuestDB", "desc": "Fast time-series", "jdbc": True},
                "materialize": {"name": "Materialize", "desc": "Streaming SQL", "jdbc": True},
                "rockset": {"name": "Rockset", "desc": "Real-time analytics", "jdbc": True},
            },
            "Data Lakes & Modern Formats": {
                "iceberg": {"name": "Apache Iceberg", "desc": "Table format", "jdbc": True},
            },
            "Specialized & Emerging": {
                "singlestore": {"name": "SingleStore", "desc": "Real-time analytics", "jdbc": True},
                "neo4j": {"name": "Neo4j", "desc": "Graph database", "jdbc": True},
                "mindsdb": {"name": "MindsDB", "desc": "ML database", "jdbc": True},
            },
        }

    def ask_for_adapter_choice_enhanced(self, prompt_prefix: str = "") -> str:
        """Enhanced adapter selection with categories."""
        metadata = self.get_adapter_metadata()
        menu_lines = []
        adapter_list = []
        counter = 1

        for category, adapters in metadata.items():
            menu_lines.append(f"\n{category}:")
            for adapter_key, info in adapters.items():
                jdbc = " [JDBC]" if info["jdbc"] else ""
                menu_lines.append(f"  [{counter}] {info['name']}{jdbc} - {info['desc']}")
                adapter_list.append(adapter_key)
                counter += 1

        prompt_msg = (
            f"{prompt_prefix}" + "\n".join(menu_lines) +
            "\n\nAll adapters support Spark JDBC federation\nEnter a number"
        )

        numeric_choice = click.prompt(prompt_msg, type=click.INT)
        return adapter_list[numeric_choice - 1]

    def ask_for_multi_connection_setup(self) -> bool:
        """Ask if user wants multi-connection setup."""
        msg = (
            "\nDVT supports multi-source data federation.\n"
            "Set up multiple database connections?\n"
            "  [1] Yes - Multiple connections (recommended for federation)\n"
            "  [2] No - Single connection (can add more later)\n"
            "\nEnter a number"
        )
        choice = click.prompt(msg, type=click.INT, default=1)
        return choice == 1

    def setup_multi_connection_profile(self, profile_name: str) -> int:
        """
        Set up profile with multiple connections interactively.
        Returns number of connections configured.
        """
        fire_event(SettingUpProfile())

        if not self.check_if_can_write_profile(profile_name=profile_name):
            return 0

        # Ask how many
        num = click.prompt(
            "\nHow many database connections? (1-10)",
            type=click.INT,
            default=2
        )
        num = max(1, min(10, num))

        outputs = {}

        for i in range(num):
            click.echo(f"\n--- Connection {i+1}/{num} ---")

            adapter = self.ask_for_adapter_choice_enhanced(
                prompt_prefix=f"\nSelect database type for connection {i+1}:\n"
            )

            default_name = f"{adapter}_{i+1}" if i > 0 else adapter
            conn_name = click.prompt(
                f"Connection name",
                default=default_name
            )

            # Use adapter's profile template for prompts
            load_plugin(adapter)
            adapter_path = get_include_paths(adapter)[0]
            template_path = adapter_path / "profile_template.yml"

            if template_path.exists():
                with open(template_path) as f:
                    template = yaml.safe_load(f)
                prompts = template.get("prompts", {})
                fixed = template.get("fixed", {})
                target_config = self.generate_target_from_input(prompts, fixed)
                target_config.pop("target", None)
                outputs[conn_name] = target_config
            else:
                outputs[conn_name] = {"type": adapter}

        # Set default target
        output_names = list(outputs.keys())
        default_target = output_names[0]

        if len(output_names) > 1:
            click.echo("\nAvailable connections:")
            for idx, name in enumerate(output_names):
                click.echo(f"  [{idx+1}] {name}")

            default_choice = click.prompt(
                "\nDefault target? (enter number)",
                type=click.INT,
                default=1
            )
            default_target = output_names[max(0, min(default_choice - 1, len(output_names) - 1))]

        # Write profile
        profile = {"outputs": outputs, "target": default_target}
        self.write_profile(profile, profile_name)

        profiles_path = Path(get_flags().PROFILES_DIR) / "profiles.yml"
        fire_event(ProfileWrittenWithTargetTemplateYAML(name=profile_name, path=str(profiles_path)))

        return len(outputs)

    def show_next_steps(self, project_name: str, num_connections: int) -> None:
        """Show helpful next steps."""
        click.echo("\n" + "=" * 60)
        click.echo("🎉 DVT project initialized successfully!")
        click.echo("=" * 60)
        click.echo(f"\nProject: {project_name}")
        click.echo(f"Connections: {num_connections} configured")
        click.echo("\n🚀 Next Steps:")
        click.echo(f"  1. cd {project_name}")
        click.echo("  2. Edit models/example/my_first_dbt_model.sql")
        click.echo("  3. dvt run")
        click.echo("  4. dvt test")
        click.echo("\n🔗 Useful Commands:")
        click.echo("  dvt target list       # List connections")
        click.echo("  dvt target test-all   # Test all connections")
        click.echo("  dvt compute list      # Show Spark config")
        click.echo("  dvt --help            # See all commands")
        click.echo("\n" + "=" * 60)

    def get_valid_project_name(self) -> str:
        """Returns a valid project name, either from CLI arg or user prompt."""

        # Lazy import to avoid ModuleNotFoundError
        from dbt.include.global_project import PROJECT_NAME as GLOBAL_PROJECT_NAME

        name = self.args.project_name
        internal_package_names = {GLOBAL_PROJECT_NAME}
        available_adapters = list(_get_adapter_plugin_names())
        for adapter_name in available_adapters:
            internal_package_names.update(f"dbt_{adapter_name}")
        while not ProjectName.is_valid(name) or name in internal_package_names:
            if name:
                click.echo(name + " is not a valid project name.")
            name = click.prompt("Enter a name for your project (letters, digits, underscore)")

        return name

    def create_new_project(self, project_name: str, profile_name: str):
        self.copy_starter_repo(project_name)
        os.chdir(project_name)
        with open("dbt_project.yml", "r") as f:
            content = f"{f.read()}".format(project_name=project_name, profile_name=profile_name)
        with open("dbt_project.yml", "w") as f:
            f.write(content)

        # Create project-level .dvt/jdbc_jars/ directory
        from dbt.config.compute import ComputeRegistry
        ComputeRegistry.ensure_jdbc_jars_dir(".")

        fire_event(
            ProjectCreated(
                project_name=project_name,
                docs_url=DOCS_URL,
                slack_url=SLACK_URL,
            )
        )

    def run(self):
        """Entry point for the init task."""
        profiles_dir = get_flags().PROFILES_DIR
        self.create_profiles_dir(profiles_dir)

        try:
            move_to_nearest_project_dir(self.args.project_dir)
            in_project = True
        except dbt_common.exceptions.DbtRuntimeError:
            in_project = False

        if in_project:
            # If --profile was specified, it means use an existing profile, which is not
            # applicable to this case
            if self.args.profile:
                raise DbtRuntimeError(
                    msg="Can not init existing project with specified profile, edit dbt_project.yml instead"
                )

            # Ensure project-level .dvt/jdbc_jars/ directory exists
            from dbt.config.compute import ComputeRegistry
            ComputeRegistry.ensure_jdbc_jars_dir(".")

            # When dbt init is run inside an existing project,
            # just setup the user's profile.
            if not self.args.skip_profile_setup:
                # Get profile name from dbt_project.yml
                profile_name = self.get_profile_name_from_current_project()
                self.setup_profile(profile_name)
        else:
            # When dbt init is run outside of an existing project,
            # create a new project and set up the user's profile.
            project_name = self.get_valid_project_name()
            project_path = Path(project_name)
            if project_path.exists():
                fire_event(ProjectNameAlreadyExists(name=project_name))
                return

            # If the user specified an existing profile to use, use it instead of generating a new one
            user_profile_name = self.args.profile
            if user_profile_name:
                if not self.check_if_profile_exists(user_profile_name):
                    raise DbtRuntimeError(
                        msg="Could not find profile named '{}'".format(user_profile_name)
                    )
                self.create_new_project(project_name, user_profile_name)
                self.show_next_steps(project_name, 1)
            else:
                profile_name = project_name
                # Create the profile after creating the project to avoid leaving a random profile
                # if the former fails.
                self.create_new_project(project_name, profile_name)

                # DVT v0.5.1: Enhanced multi-connection init wizard
                if not self.args.skip_profile_setup:
                    # Ask about multi-connection setup
                    if self.ask_for_multi_connection_setup():
                        num_conn = self.setup_multi_connection_profile(profile_name)
                    else:
                        self.setup_profile(profile_name)
                        num_conn = 1

                    self.show_next_steps(project_name, num_conn)
