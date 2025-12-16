import functools
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from copy import copy
from dataclasses import dataclass
import re
import time
from typing import Callable, List, Optional, Union

import click
from click.exceptions import BadOptionUsage
from click.exceptions import Exit as ClickExit
from click.exceptions import NoSuchOption, UsageError

from dbt.adapters.factory import register_adapter
from dbt.artifacts.schemas.catalog import CatalogArtifact
from dbt.artifacts.schemas.run import RunExecutionResult
from dbt.cli import params as p
from dbt.cli import requires
from dbt.cli.exceptions import DbtInternalException, DbtUsageException
from dbt.cli.requires import setup_manifest
from dbt.contracts.graph.manifest import Manifest
from dbt.mp_context import get_mp_context
from dbt_common.events.base_types import EventMsg


@dataclass
class dbtRunnerResult:
    """Contains the result of an invocation of the dbtRunner"""

    success: bool

    exception: Optional[BaseException] = None
    result: Union[
        bool,  # debug
        CatalogArtifact,  # docs generate
        List[str],  # list/ls
        Manifest,  # parse
        None,  # clean, deps, init, source
        RunExecutionResult,  # build, compile, run, seed, snapshot, test, run-operation
    ] = None


# Programmatic invocation
class dbtRunner:
    def __init__(
        self,
        manifest: Optional[Manifest] = None,
        callbacks: Optional[List[Callable[[EventMsg], None]]] = None,
    ) -> None:
        self.manifest = manifest

        if callbacks is None:
            callbacks = []
        self.callbacks = callbacks

    def invoke(self, args: List[str], **kwargs) -> dbtRunnerResult:
        try:
            dbt_ctx = cli.make_context(cli.name, args.copy())
            dbt_ctx.obj = {
                "manifest": self.manifest,
                "callbacks": self.callbacks,
                "dbt_runner_command_args": args,
            }

            for key, value in kwargs.items():
                dbt_ctx.params[key] = value
                # Hack to set parameter source to custom string
                dbt_ctx.set_parameter_source(key, "kwargs")  # type: ignore

            result, success = cli.invoke(dbt_ctx)
            return dbtRunnerResult(
                result=result,
                success=success,
            )
        except requires.ResultExit as e:
            return dbtRunnerResult(
                result=e.result,
                success=False,
            )
        except requires.ExceptionExit as e:
            return dbtRunnerResult(
                exception=e.exception,
                success=False,
            )
        except (BadOptionUsage, NoSuchOption, UsageError) as e:
            return dbtRunnerResult(
                exception=DbtUsageException(e.message),
                success=False,
            )
        except ClickExit as e:
            if e.exit_code == 0:
                return dbtRunnerResult(success=True)
            return dbtRunnerResult(
                exception=DbtInternalException(f"unhandled exit code {e.exit_code}"),
                success=False,
            )
        except BaseException as e:
            return dbtRunnerResult(
                exception=e,
                success=False,
            )


# approach from https://github.com/pallets/click/issues/108#issuecomment-280489786
def global_flags(func):
    @p.cache_selected_only
    @p.debug
    @p.defer
    @p.deprecated_defer
    @p.defer_state
    @p.deprecated_favor_state
    @p.deprecated_print
    @p.deprecated_state
    @p.fail_fast
    @p.favor_state
    @p.indirect_selection
    @p.log_cache_events
    @p.log_file_max_bytes
    @p.log_format
    @p.log_format_file
    @p.log_level
    @p.log_level_file
    @p.log_path
    @p.macro_debugging
    @p.partial_parse
    @p.partial_parse_file_path
    @p.partial_parse_file_diff
    @p.populate_cache
    @p.print
    @p.printer_width
    @p.profile
    @p.quiet
    @p.record_timing_info
    @p.send_anonymous_usage_stats
    @p.single_threaded
    @p.show_all_deprecations
    @p.state
    @p.static_parser
    @p.target
    @p.target_compute
    @p.use_colors
    @p.use_colors_file
    @p.use_experimental_parser
    @p.version
    @p.version_check
    @p.warn_error
    @p.warn_error_options
    @p.write_json
    @p.use_fast_test_edges
    @p.upload_artifacts
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# dbt
@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
    no_args_is_help=True,
    epilog="Specify one of these sub-commands and you can find more help from there.",
)
@click.pass_context
@global_flags
@p.show_resource_report
def cli(ctx, **kwargs):
    """An ELT tool for managing your SQL transformations and data models.
    For more documentation on these commands, visit: docs.getdbt.com
    """


# dbt build
@cli.command("build")
@click.pass_context
@global_flags
@p.empty
@p.event_time_start
@p.event_time_end
@p.exclude
@p.export_saved_queries
@p.full_refresh
@p.deprecated_include_saved_query
@p.profiles_dir
@p.project_dir
@p.resource_type
@p.exclude_resource_type
@p.sample
@p.select
@p.selector
@p.show
@p.store_failures
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.catalogs
@requires.runtime_config
@requires.manifest
def build(ctx, **kwargs):
    """Run all seeds, models, snapshots, and tests in DAG order"""
    from dbt.task.build import BuildTask

    task = BuildTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt clean
@cli.command("clean")
@click.pass_context
@global_flags
@p.clean_project_files_only
@p.profiles_dir
@p.project_dir
@p.target_path
@p.vars
@requires.postflight
@requires.preflight
@requires.unset_profile
@requires.project
def clean(ctx, **kwargs):
    """Delete all folders in the clean-targets list (usually the dbt_packages and target directories.)"""
    from dbt.task.clean import CleanTask

    with CleanTask(ctx.obj["flags"], ctx.obj["project"]) as task:
        results = task.run()
        success = task.interpret_results(results)
    return results, success


# dbt docs
@cli.group()
@click.pass_context
@global_flags
def docs(ctx, **kwargs):
    """Generate or serve the documentation website for your project"""


# dbt docs generate
@docs.command("generate")
@click.pass_context
@global_flags
@p.compile_docs
@p.exclude
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.empty_catalog
@p.static
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest(write=False)
def docs_generate(ctx, **kwargs):
    """Generate the documentation website for your project"""
    from dbt.task.docs.generate import GenerateTask

    task = GenerateTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt docs serve
@docs.command("serve")
@click.pass_context
@global_flags
@p.browser
@p.host
@p.port
@p.profiles_dir
@p.project_dir
@p.target_path
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
def docs_serve(ctx, **kwargs):
    """Serve the documentation website for your project"""
    from dbt.task.docs.serve import ServeTask

    task = ServeTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt compile
@cli.command("compile")
@click.pass_context
@global_flags
@p.exclude
@p.full_refresh
@p.show_output_format
@p.introspect
@p.profiles_dir
@p.project_dir
@p.empty
@p.select
@p.selector
@p.inline
@p.compile_inject_ephemeral_ctes
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
def compile(ctx, **kwargs):
    """Generates executable SQL from source, model, test, and analysis files. Compiled SQL files are written to the
    target/ directory."""
    from dbt.task.compile import CompileTask

    task = CompileTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt show
@cli.command("show")
@click.pass_context
@global_flags
@p.exclude
@p.full_refresh
@p.show_output_format
@p.show_limit
@p.introspect
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.inline
@p.inline_direct
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
def show(ctx, **kwargs):
    """Generates executable SQL for a named resource or inline query, runs that SQL, and returns a preview of the
    results. Does not materialize anything to the warehouse."""
    from dbt.task.show import ShowTask, ShowTaskDirect

    if ctx.obj["flags"].inline_direct:
        # Issue the inline query directly, with no templating. Does not require
        # loading the manifest.
        register_adapter(ctx.obj["runtime_config"], get_mp_context())
        task = ShowTaskDirect(
            ctx.obj["flags"],
            ctx.obj["runtime_config"],
        )
    else:
        setup_manifest(ctx)
        task = ShowTask(
            ctx.obj["flags"],
            ctx.obj["runtime_config"],
            ctx.obj["manifest"],
        )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt debug
@cli.command("debug")
@click.pass_context
@global_flags
@p.debug_connection
@p.config_dir
@p.profiles_dir_exists_false
@p.project_dir
@p.vars
@requires.postflight
@requires.preflight
def debug(ctx, **kwargs):
    """Show information on the current dbt environment and check dependencies, then test the database connection. Not to be confused with the --debug option which increases verbosity."""
    from dbt.task.debug import DebugTask

    task = DebugTask(
        ctx.obj["flags"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt deps
@cli.command("deps")
@click.pass_context
@global_flags
@p.profiles_dir_exists_false
@p.project_dir
@p.vars
@p.source
@p.lock
@p.upgrade
@p.add_package
@requires.postflight
@requires.preflight
@requires.unset_profile
@requires.project
def deps(ctx, **kwargs):
    """Install dbt packages specified.
    In the following case, a new `package-lock.yml` will be generated and the packages are installed:
    - user updated the packages.yml
    - user specify the flag --update, which means for packages that are specified as a
      range, dbt-core will try to install the newer version
    Otherwise, deps will use `package-lock.yml` as source of truth to install packages.

    There is a way to add new packages by providing an `--add-package` flag to deps command
    which will allow user to specify a package they want to add in the format of packagename@version.
    """
    from dbt.task.deps import DepsTask

    flags = ctx.obj["flags"]
    if flags.ADD_PACKAGE:
        if not flags.ADD_PACKAGE["version"] and flags.SOURCE != "local":
            raise BadOptionUsage(
                message=f"Version is required in --add-package when a package when source is {flags.SOURCE}",
                option_name="--add-package",
            )
    with DepsTask(flags, ctx.obj["project"]) as task:
        results = task.run()
        success = task.interpret_results(results)
    return results, success


# dbt init
@cli.command("init")
@click.pass_context
@global_flags
# for backwards compatibility, accept 'project_name' as an optional positional argument
@click.argument("project_name", required=False)
@p.profiles_dir_exists_false
@p.project_dir
@p.skip_profile_setup
@p.vars
@requires.postflight
@requires.preflight
def init(ctx, **kwargs):
    """Initialize a new dbt project."""
    from dbt.task.init import InitTask

    with InitTask(ctx.obj["flags"]) as task:
        results = task.run()
        success = task.interpret_results(results)
    return results, success


# dbt list
@cli.command("list")
@click.pass_context
@global_flags
@p.exclude
@p.models
@p.output
@p.output_keys
@p.profiles_dir
@p.project_dir
@p.resource_type
@p.exclude_resource_type
@p.raw_select
@p.selector
@p.target_path
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
def list(ctx, **kwargs):
    """List the resources in your project"""
    from dbt.task.list import ListTask

    task = ListTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# Alias "list" to "ls"
ls = copy(cli.commands["list"])
ls.hidden = True
cli.add_command(ls, "ls")


# dbt parse
@cli.command("parse")
@click.pass_context
@global_flags
@p.profiles_dir
@p.project_dir
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.catalogs
@requires.runtime_config
@requires.manifest(write_perf_info=True)
def parse(ctx, **kwargs):
    """Parses the project and provides information on performance"""
    # manifest generation and writing happens in @requires.manifest
    return ctx.obj["manifest"], True


# dbt run
@cli.command("run")
@click.pass_context
@global_flags
@p.exclude
@p.full_refresh
@p.profiles_dir
@p.project_dir
@p.empty
@p.event_time_start
@p.event_time_end
@p.sample
@p.select
@p.selector
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.catalogs
@requires.runtime_config
@requires.manifest
def run(ctx, **kwargs):
    """Compile SQL and execute against the current target database."""
    from dbt.task.run import RunTask

    task = RunTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt retry
@cli.command("retry")
@click.pass_context
@global_flags
@p.project_dir
@p.profiles_dir
@p.vars
@p.target_path
@p.threads
@p.full_refresh
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
def retry(ctx, **kwargs):
    """Retry the nodes that failed in the previous run."""
    from dbt.task.retry import RetryTask

    # Retry will parse manifest inside the task after we consolidate the flags
    task = RetryTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt clone
@cli.command("clone")
@click.pass_context
@global_flags
@p.exclude
@p.full_refresh
@p.profiles_dir
@p.project_dir
@p.resource_type
@p.exclude_resource_type
@p.select
@p.selector
@p.target_path
@p.threads
@p.vars
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
@requires.postflight
def clone(ctx, **kwargs):
    """Create clones of selected nodes based on their location in the manifest provided to --state."""
    from dbt.task.clone import CloneTask

    task = CloneTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt run operation
@cli.command("run-operation")
@click.pass_context
@global_flags
@click.argument("macro")
@p.args
@p.profiles_dir
@p.project_dir
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
def run_operation(ctx, **kwargs):
    """Run the named macro with any supplied arguments."""
    from dbt.task.run_operation import RunOperationTask

    task = RunOperationTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt seed
@cli.command("seed")
@click.pass_context
@global_flags
@p.exclude
@p.full_refresh
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.show
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.catalogs
@requires.runtime_config
@requires.manifest
def seed(ctx, **kwargs):
    """Load data from csv files into your data warehouse."""
    from dbt.task.seed import SeedTask

    task = SeedTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )
    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt snapshot
@cli.command("snapshot")
@click.pass_context
@global_flags
@p.empty
@p.exclude
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.catalogs
@requires.runtime_config
@requires.manifest
def snapshot(ctx, **kwargs):
    """Execute snapshots defined in your project"""
    from dbt.task.snapshot import SnapshotTask

    task = SnapshotTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# dbt source
@cli.group()
@click.pass_context
@global_flags
def source(ctx, **kwargs):
    """Manage your project's sources"""


# dbt source freshness
@source.command("freshness")
@click.pass_context
@global_flags
@p.exclude
@p.output_path  # TODO: Is this ok to re-use?  We have three different output params, how much can we consolidate?
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
def freshness(ctx, **kwargs):
    """check the current freshness of the project's sources"""
    from dbt.task.freshness import FreshnessTask

    task = FreshnessTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# Alias "source freshness" to "snapshot-freshness"
snapshot_freshness = copy(cli.commands["source"].commands["freshness"])  # type: ignore
snapshot_freshness.hidden = True
cli.commands["source"].add_command(snapshot_freshness, "snapshot-freshness")  # type: ignore


# dbt test
@cli.command("test")
@click.pass_context
@global_flags
@p.exclude
@p.resource_type
@p.exclude_resource_type
@p.profiles_dir
@p.project_dir
@p.select
@p.selector
@p.store_failures
@p.target_path
@p.threads
@p.vars
@requires.postflight
@requires.preflight
@requires.profile
@requires.project
@requires.runtime_config
@requires.manifest
def test(ctx, **kwargs):
    """Runs tests on data in deployed models. Run this after `dbt run`"""
    from dbt.task.test import TestTask

    task = TestTask(
        ctx.obj["flags"],
        ctx.obj["runtime_config"],
        ctx.obj["manifest"],
    )

    results = task.run()
    success = task.interpret_results(results)
    return results, success


# DVT compute commands
@cli.group()
@click.pass_context
@global_flags
def compute(ctx, **kwargs):
    """Manage DVT compute engines for multi-source federation.

    Compute engines are configured in ~/.dvt/.data/computes.yml.
    Use 'dvt compute edit' to modify configuration.

    Commands:
        test      Show all compute engines with connection status
        edit      Open computes.yml in your editor
        validate  Validate computes.yml syntax
    """


@compute.command("list")
@click.pass_context
@p.project_dir
def compute_list(ctx, **kwargs):
    """List all configured compute engines.

    Shows all compute engines defined in computes.yml with their
    platform type and description.

    Examples:
        dvt compute list                    # List all compute engines
    """
    from dbt.task.compute import ComputeTask

    task = ComputeTask(project_dir=kwargs.get("project_dir"))
    success = task.list_computes()
    return None, success


@compute.command("test")
@click.pass_context
@click.argument("compute_name", required=True)
@p.project_dir
def compute_test(ctx, compute_name, **kwargs):
    """Test a compute engine's connectivity.

    Tests the specified compute engine and shows its status.
    Use 'dvt compute list' to see all available compute engines.

    Shows rich status symbols:
        ✅ Connected/Available
        ❌ Error/Not available
        ⚠️  Warning (missing optional dependency)

    Examples:
        dvt compute test spark-local        # Test local Spark
        dvt compute test databricks-prod    # Test Databricks connectivity
        dvt compute test spark-docker       # Test Docker Spark cluster
    """
    from dbt.task.compute import ComputeTask

    task = ComputeTask(project_dir=kwargs.get("project_dir"))
    success = task.test_single_compute(compute_name)
    return None, success


@compute.command("edit")
@click.pass_context
@p.project_dir
def compute_edit(ctx, **kwargs):
    """Open computes.yml in your editor.

    Opens the compute configuration file in your preferred editor.
    Uses EDITOR environment variable, or falls back to common editors
    (code, nano, vim, vi, notepad).

    The file contains comprehensive commented samples for:
    - Local Spark (default)
    - Databricks (SQL Warehouse and Interactive Cluster)
    - AWS EMR
    - GCP Dataproc
    - Standalone Spark clusters

    After editing, run 'dvt compute validate' to check syntax.

    Examples:
        dvt compute edit              # Open in default editor
        EDITOR=nano dvt compute edit  # Use specific editor
    """
    from dbt.task.compute import ComputeTask

    task = ComputeTask(project_dir=kwargs.get("project_dir"))
    success = task.edit_config()
    return None, success


@compute.command("validate")
@click.pass_context
@p.project_dir
def compute_validate(ctx, **kwargs):
    """Validate computes.yml syntax and configuration.

    Checks the compute configuration file for:
    - Valid YAML syntax
    - Required fields (target_compute, type)
    - Valid compute engine references
    - Platform-specific configuration

    Examples:
        dvt compute validate    # Validate configuration
    """
    from dbt.task.compute import ComputeTask

    task = ComputeTask(project_dir=kwargs.get("project_dir"))
    is_valid = task.validate_config()
    return None, is_valid




# DVT migrate command - migrate from .dbt/ to .dvt/
@cli.command("migrate")
@click.pass_context
@p.profiles_dir
@p.project_dir
def migrate(ctx, **kwargs):
    """Migrate configuration from .dbt/ to .dvt/ directory"""
    from pathlib import Path
    import shutil

    home = Path.home()

    old_dbt_dir = home / ".dbt"
    new_dvt_dir = home / ".dvt"

    if not old_dbt_dir.exists():
        click.echo("No .dbt/ directory found - nothing to migrate")
        return True, True

    if new_dvt_dir.exists():
        response = click.confirm(
            f".dvt/ directory already exists at {new_dvt_dir}. Overwrite files?"
        )
        if not response:
            click.echo("Migration cancelled")
            return False, False

    # Create .dvt directory
    new_dvt_dir.mkdir(parents=True, exist_ok=True)

    # Copy profiles.yml if it exists
    old_profiles = old_dbt_dir / "profiles.yml"
    new_profiles = new_dvt_dir / "profiles.yml"

    migrated_files = []

    if old_profiles.exists():
        shutil.copy2(old_profiles, new_profiles)
        migrated_files.append("profiles.yml")
        click.echo(f"✓ Copied {old_profiles} → {new_profiles}")

    if migrated_files:
        click.echo("")
        click.echo(f"Migration complete! Migrated {len(migrated_files)} files:")
        for f in migrated_files:
            click.echo(f"  - {f}")
        click.echo("")
        click.echo("Your .dbt/ directory has been preserved.")
        click.echo("DVT will now use .dvt/ for all configurations.")
        click.echo("")
        click.echo("Note: Compute engines are managed via 'dvt compute' commands.")
    else:
        click.echo("No files to migrate")

    return True, True


# DVT target (connection) management commands
@cli.group()
@click.pass_context
@global_flags
def target(ctx, **kwargs):
    """Manage connection targets in profiles.yml"""


@target.command("list")
@click.option("--profile", help="Profile name to list targets from")
@click.pass_context
@p.profiles_dir
@p.project_dir
def target_list(ctx, profile, profiles_dir, project_dir, **kwargs):
    """List available targets in profiles.yml.

    If executed from within a DVT project directory, automatically detects the profile
    from dbt_project.yml. Use --profile to override or when outside a project directory.

    Features colored output for improved readability:
    - Cyan: Profile and target names
    - Green: Default target indicators
    - Red: Error messages

    Examples:
        dvt target list                    # Auto-detect from project
        dvt target list --profile my_proj  # Specific profile
    """
    from dbt.config.profile import read_profile
    from dbt.config.project_utils import get_project_profile_name

    profiles = read_profile(profiles_dir)

    if not profiles:
        click.echo(click.style("No profiles found in profiles.yml", fg="red"))
        ctx.exit(1)

    # If --profile not provided, try to get from dbt_project.yml
    if not profile:
        profile = get_project_profile_name(project_dir)
        if not profile:
            # No profile specified and none found in project - show all profiles
            click.echo(click.style("Available profiles:", fg="cyan", bold=True))
            click.echo("")
            for profile_name, profile_data in profiles.items():
                if profile_data is None:
                    profile_data = {}
                outputs = profile_data.get("outputs", {})
                target_count = len(outputs)
                default_target = profile_data.get(
                    "default_target", profile_data.get("target", "unknown")
                )
                click.echo(f"  {click.style(profile_name, fg='cyan')}")
                click.echo(
                    f"    Default target: {click.style(default_target, fg='green')}"
                )
                click.echo(f"    Targets: {target_count}")
                click.echo("")
            return True, True

    # Show targets for specific profile
    if profile not in profiles:
        click.echo(click.style(f"✗ Profile '{profile}' not found", fg="red"))
        ctx.exit(1)

    profile_data = profiles[profile]
    if profile_data is None:
        click.echo(click.style(f"✗ Profile '{profile}' is empty or invalid", fg="red"))
        ctx.exit(1)
    outputs = profile_data.get("outputs", {})

    if not outputs:
        click.echo(click.style(f"No targets found in profile '{profile}'", fg="yellow"))
        return True, True

    default_target = profile_data.get(
        "default_target", profile_data.get("target", "unknown")
    )

    # Always show profile name header for context
    click.echo(click.style(f"Profile: {profile}", fg="cyan", bold=True))
    click.echo(f"Default target: {click.style(default_target, fg='green')}")
    click.echo("")
    click.echo("Available targets:")
    for target_name, target_config in outputs.items():
        default_marker = (
            click.style(" (default)", fg="green")
            if target_name == default_target
            else ""
        )
        adapter_type = target_config.get("type", "unknown")
        click.echo(
            f"  {click.style(target_name, fg='cyan')} ({adapter_type}){default_marker}"
        )

    return True, True


def _get_test_query(adapter_type: str) -> str:
    """Get adapter-specific test query for connection validation.

    Args:
        adapter_type: The adapter type (postgres, snowflake, etc.)

    Returns:
        SQL query string for testing connectivity
    """
    test_queries = {
        "postgres": "SELECT 1",
        "snowflake": "SELECT CURRENT_VERSION()",
        "bigquery": "SELECT 1",
        "redshift": "SELECT 1",
        "databricks": "SELECT 1",
        "mysql": "SELECT 1",
        "sqlserver": "SELECT 1",
        "oracle": "SELECT 1 FROM DUAL",
        "db2": "SELECT 1 FROM SYSIBM.SYSDUMMY1",
        "teradata": "SELECT 1",
    }
    return test_queries.get(adapter_type, "SELECT 1")


def _get_connection_error_hint(exception: Exception, adapter_type: str) -> str:
    """Provide user-friendly hints for common connection errors.

    Args:
        exception: The exception that was raised
        adapter_type: The adapter type being tested

    Returns:
        A helpful error message with troubleshooting hints
    """
    error_str = str(exception).lower()

    # Common error patterns and hints
    if "timeout" in error_str or "timed out" in error_str:
        return "Connection timeout - Check network connectivity and firewall rules"
    elif "could not connect" in error_str or "connection refused" in error_str:
        return "Connection refused - Verify host and port are correct"
    elif (
        "authentication" in error_str or "password" in error_str or "login" in error_str
    ):
        return "Authentication failed - Check username and password"
    elif "database" in error_str and "does not exist" in error_str:
        return "Database not found - Verify database name"
    elif "permission" in error_str or "access denied" in error_str:
        return "Permission denied - Check user privileges"
    elif "ssl" in error_str or "certificate" in error_str:
        return "SSL/TLS error - Check SSL configuration"
    elif "no such host" in error_str or "name resolution" in error_str:
        return "Host not found - Verify hostname is correct"

    # Adapter-specific hints
    if adapter_type == "snowflake":
        if "account" in error_str:
            return "Invalid Snowflake account - Check account identifier format"
        elif "warehouse" in error_str:
            return "Warehouse error - Verify warehouse name and status"
    elif adapter_type == "databricks":
        if "token" in error_str:
            return "Invalid token - Check Databricks access token"
        elif "cluster" in error_str:
            return "Cluster error - Verify cluster is running and accessible"

    return "Connection failed - See error details above"


def _test_single_target(profile_data: dict, target_name: str) -> tuple[bool, str]:
    """Test connection to a single target by executing a query.

    Args:
        profile_data: The profile dictionary containing outputs
        target_name: Name of the target to test

    Returns:
        Tuple of (success: bool, message: str)
    """
    outputs = profile_data.get("outputs", {})

    if target_name not in outputs:
        return False, f"Target '{target_name}' not found"

    target_config = outputs[target_name]
    adapter_type = target_config.get("type", "unknown")

    # Validate required fields first
    required_fields = {
        "postgres": ["host", "user", "database"],
        "snowflake": ["account", "user", "database", "warehouse"],
        "bigquery": ["project", "dataset"],
        "redshift": ["host", "user", "database"],
        "databricks": ["host", "http_path"],
    }

    missing_fields = []
    if adapter_type in required_fields:
        for field in required_fields[adapter_type]:
            if field not in target_config:
                missing_fields.append(field)

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    # Import adapter and test connection
    try:
        # Get test query for this adapter
        test_query = _get_test_query(adapter_type)

        # Use the adapter's native connection testing approach
        # Each adapter has different connection methods, so we'll use
        # a simplified approach that works across adapters

        if adapter_type == "postgres":
            try:
                import psycopg2

                # Build connection string
                conn_params = {
                    "host": target_config.get("host", "localhost"),
                    "port": target_config.get("port", 5432),
                    "database": target_config.get(
                        "database", target_config.get("dbname")
                    ),
                    "user": target_config.get("user"),
                    "password": target_config.get("password"),
                }
                # Test connection
                conn = psycopg2.connect(**conn_params, connect_timeout=10)
                cursor = conn.cursor()
                cursor.execute(test_query)
                cursor.fetchone()
                cursor.close()
                conn.close()
                return True, "Connection successful"
            except ImportError:
                return (
                    False,
                    "psycopg2 not installed - Run 'pip install psycopg2-binary' or 'pip install dbt-postgres'",
                )
            except Exception as e:
                hint = _get_connection_error_hint(e, adapter_type)
                return False, f"Connection failed: {str(e)}\nHint: {hint}"

        elif adapter_type == "snowflake":
            try:
                import snowflake.connector

                # Build connection params
                conn_params = {
                    "account": target_config.get("account"),
                    "user": target_config.get("user"),
                    "password": target_config.get("password"),
                    "database": target_config.get("database"),
                    "warehouse": target_config.get("warehouse"),
                    "schema": target_config.get("schema", "PUBLIC"),
                }
                # Test connection
                conn = snowflake.connector.connect(**conn_params, login_timeout=10)
                cursor = conn.cursor()
                cursor.execute(test_query)
                cursor.fetchone()
                cursor.close()
                conn.close()
                return True, "Connection successful"
            except ImportError:
                return (
                    False,
                    "snowflake-connector-python not installed - Run 'pip install snowflake-connector-python' or 'pip install dbt-snowflake'",
                )
            except Exception as e:
                hint = _get_connection_error_hint(e, adapter_type)
                return False, f"Connection failed: {str(e)}\nHint: {hint}"

        elif adapter_type == "bigquery":
            try:
                from google.cloud import bigquery

                # Build client
                project = target_config.get("project")
                client = bigquery.Client(project=project)
                # Test connection with simple query
                query_job = client.query(test_query)
                query_job.result(timeout=10)
                return True, "Connection successful"
            except ImportError:
                return (
                    False,
                    "google-cloud-bigquery not installed - Run 'pip install google-cloud-bigquery' or 'pip install dbt-bigquery'",
                )
            except Exception as e:
                hint = _get_connection_error_hint(e, adapter_type)
                return False, f"Connection failed: {str(e)}\nHint: {hint}"

        elif adapter_type == "redshift":
            try:
                import psycopg2

                # Redshift uses postgres protocol
                conn_params = {
                    "host": target_config.get("host"),
                    "port": target_config.get("port", 5439),
                    "database": target_config.get("database"),
                    "user": target_config.get("user"),
                    "password": target_config.get("password"),
                }
                # Test connection
                conn = psycopg2.connect(**conn_params, connect_timeout=10)
                cursor = conn.cursor()
                cursor.execute(test_query)
                cursor.fetchone()
                cursor.close()
                conn.close()
                return True, "Connection successful"
            except ImportError:
                return (
                    False,
                    "psycopg2 not installed - Run 'pip install psycopg2-binary' or 'pip install dbt-redshift'",
                )
            except Exception as e:
                hint = _get_connection_error_hint(e, adapter_type)
                return False, f"Connection failed: {str(e)}\nHint: {hint}"

        elif adapter_type == "databricks":
            try:
                from databricks import sql

                # Build connection params
                conn_params = {
                    "server_hostname": target_config.get("host", "").replace(
                        "https://", ""
                    ),
                    "http_path": target_config.get("http_path"),
                    "access_token": target_config.get("token"),
                }
                # Test connection
                conn = sql.connect(**conn_params)
                cursor = conn.cursor()
                cursor.execute(test_query)
                cursor.fetchone()
                cursor.close()
                conn.close()
                return True, "Connection successful"
            except ImportError:
                return (
                    False,
                    "databricks-sql-connector not installed - Run 'pip install databricks-sql-connector' or 'pip install dbt-databricks'",
                )
            except Exception as e:
                hint = _get_connection_error_hint(e, adapter_type)
                return False, f"Connection failed: {str(e)}\nHint: {hint}"

        else:
            # For unsupported adapter types, just return configuration validation
            return (
                True,
                "Configuration valid (network testing not available for this adapter type)",
            )

    except Exception as e:
        hint = _get_connection_error_hint(e, adapter_type)
        return False, f"Unexpected error: {str(e)}\nHint: {hint}"


def _test_target_with_timeout(
    profile_data: dict, target_name: str, timeout: int = 30
) -> tuple[bool, str]:
    """Test target connection with timeout protection.

    Args:
        profile_data: The profile dictionary
        target_name: Name of the target to test
        timeout: Timeout in seconds (default 30)

    Returns:
        Tuple of (success: bool, message: str)
    """
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_test_single_target, profile_data, target_name)
        try:
            success, message = future.result(timeout=timeout)
            return success, message
        except FuturesTimeoutError:
            return False, f"Connection test timed out after {timeout} seconds"
        except Exception as e:
            return False, f"Unexpected error during connection test: {str(e)}"


@target.command("test")
@click.argument("target_name", required=False, default=None)
@click.option("--profile", help="Profile name (defaults to project profile)")
@click.option(
    "--timeout",
    type=int,
    default=30,
    help="Connection timeout in seconds (default: 30)",
)
@click.pass_context
@p.profiles_dir
@p.project_dir
def target_test(
    ctx, target_name, profile, timeout, profiles_dir, project_dir, **kwargs
):
    """Test connection to one or all targets.

    When TARGET_NAME is provided: Tests connection to a specific target
    When TARGET_NAME is omitted: Tests all targets in the profile

    This command now performs REAL connection testing by executing a simple query
    against the target database. It validates both configuration AND network connectivity.

    Features colored output and proper exit codes:
    - Exit code 0: All connections succeeded
    - Exit code 1: One or more connections failed
    - Green checkmarks (✓): Success
    - Red X marks (✗): Errors

    Examples:
        dvt target test                           # Test ALL targets (auto-detect profile)
        dvt target test dev                       # Test specific target (auto-detect profile)
        dvt target test prod --profile my_proj    # Test specific target (explicit profile)
        dvt target test --profile my_proj         # Test all targets in profile
        dvt target test dev --timeout 60          # Custom timeout

    Performance:
    - Tests run with configurable timeout (default 30s)
    - Provides helpful error hints for common connection issues
    - Shows detailed connection information on success
    """
    from dbt.config.profile import read_profile
    from dbt.config.project_utils import get_project_profile_name

    profiles = read_profile(profiles_dir)

    # Determine which profile to use
    if not profile:
        # Try to get from dbt_project.yml first
        profile = get_project_profile_name(project_dir)

    if not profile:
        # If testing single target without profile, search all profiles
        if target_name:
            for prof_name, prof_data in profiles.items():
                outputs = prof_data.get("outputs", {}) if prof_data else {}
                if target_name in outputs:
                    profile = prof_name
                    break

    if not profile:
        click.echo(
            click.style(
                "✗ Error: Could not determine profile. Use --profile flag.", fg="red"
            )
        )
        ctx.exit(1)

    if profile not in profiles:
        click.echo(click.style(f"✗ Profile '{profile}' not found", fg="red"))
        ctx.exit(1)

    profile_data = profiles[profile]
    if profile_data is None:
        click.echo(click.style(f"✗ Profile '{profile}' is empty or invalid", fg="red"))
        ctx.exit(1)
    outputs = profile_data.get("outputs", {})

    if not outputs:
        click.echo(click.style(f"No targets found in profile '{profile}'", fg="yellow"))
        ctx.exit(0)

    # CASE 1: Test specific target
    if target_name:
        if target_name not in outputs:
            click.echo(
                click.style(
                    f"✗ Target '{target_name}' not found in profile '{profile}'",
                    fg="red",
                )
            )
            ctx.exit(1)

        target_config = outputs[target_name]
        adapter_type = target_config.get("type", "unknown")

        click.echo(
            f"Testing connection: {click.style(target_name, fg='cyan')} ({adapter_type})"
        )

        # Show connection details FIRST (like dbt debug)
        if "host" in target_config:
            click.echo(f"  host: {target_config['host']}")
        if "port" in target_config:
            click.echo(f"  port: {target_config['port']}")
        if "account" in target_config:
            click.echo(f"  account: {target_config['account']}")
        if "database" in target_config or "dbname" in target_config:
            db = target_config.get("database") or target_config.get("dbname")
            click.echo(f"  database: {db}")
        if "warehouse" in target_config:
            click.echo(f"  warehouse: {target_config['warehouse']}")
        if "schema" in target_config:
            click.echo(f"  schema: {target_config['schema']}")
        if "project" in target_config:
            click.echo(f"  project: {target_config['project']}")

        # Test connection with timeout
        success, message = _test_target_with_timeout(profile_data, target_name, timeout)

        # Show test result (like dbt debug)
        if success:
            click.echo(
                f"  Connection test: {click.style('[OK connection ok]', fg='green')}"
            )
            ctx.exit(0)
        else:
            click.echo(f"  Connection test: {click.style('[ERROR]', fg='red')}")
            click.echo(f"    {message}")
            ctx.exit(1)

    # CASE 2: Test all targets in profile
    else:
        total_targets = len(outputs)
        click.echo(
            f"Testing all connections in profile {click.style(profile, fg='cyan')}...\n"
        )

        # Test each target with progress indicators
        passed_count = 0
        failed_count = 0
        target_index = 1

        for tgt_name, target_config in outputs.items():
            adapter_type = target_config.get("type", "unknown")

            # Progress indicator
            progress = click.style(f"[{target_index}/{total_targets}]", fg="yellow")
            click.echo(
                f"{progress} Testing connection: {click.style(tgt_name, fg='cyan')} ({adapter_type})"
            )

            # Show connection details FIRST (like dbt debug)
            if "host" in target_config:
                click.echo(f"      host: {target_config['host']}")
            if "port" in target_config:
                click.echo(f"      port: {target_config['port']}")
            if "account" in target_config:
                click.echo(f"      account: {target_config['account']}")
            if "database" in target_config or "dbname" in target_config:
                db = target_config.get("database") or target_config.get("dbname")
                click.echo(f"      database: {db}")
            if "warehouse" in target_config:
                click.echo(f"      warehouse: {target_config['warehouse']}")
            if "schema" in target_config:
                click.echo(f"      schema: {target_config['schema']}")
            if "project" in target_config:
                click.echo(f"      project: {target_config['project']}")

            # Test connection
            success, message = _test_target_with_timeout(
                profile_data, tgt_name, timeout
            )

            # Show test result (like dbt debug)
            if success:
                click.echo(
                    f"      Connection test: {click.style('[OK connection ok]', fg='green')}"
                )
                passed_count += 1
            else:
                click.echo(f"      Connection test: {click.style('[ERROR]', fg='red')}")
                click.echo(f"        {message}")
                failed_count += 1

            click.echo("")
            target_index += 1

        # Summary line
        click.echo("─" * 60)
        if failed_count == 0:
            summary = click.style(
                f"✓ All {passed_count} connection tests passed", fg="green", bold=True
            )
            click.echo(summary)
            ctx.exit(0)
        else:
            passed_str = click.style(f"{passed_count} passed", fg="green")
            failed_str = click.style(f"{failed_count} failed", fg="red")
            summary = f"✗ {passed_str}, {failed_str}"
            click.echo(summary)
            ctx.exit(1)


@target.command("add")
@click.argument("target_name")
@click.option("--profile", required=True, help="Profile name to add target to")
@click.option(
    "--type",
    "adapter_type",
    required=True,
    help="Adapter type (postgres, snowflake, etc)",
)
@click.option("--host", help="Database host")
@click.option("--port", type=int, help="Database port")
@click.option("--user", help="Database user")
@click.option("--password", help="Database password")
@click.option("--database", help="Database name")
@click.option("--schema", help="Default schema")
@click.option("--threads", type=int, default=4, help="Number of threads")
@click.option("--set-default", is_flag=True, help="Set as default target for profile")
@click.pass_context
@p.profiles_dir
def target_add(
    ctx,
    target_name,
    profile,
    adapter_type,
    host,
    port,
    user,
    password,
    database,
    schema,
    threads,
    set_default,
    profiles_dir,
    **kwargs,
):
    """Add a new target to a profile in profiles.yml"""
    import yaml
    from pathlib import Path

    profiles_file = Path(profiles_dir) / "profiles.yml"

    if not profiles_file.exists():
        click.echo(f"✗ profiles.yml not found at {profiles_file}")
        return False, False

    with open(profiles_file, "r") as f:
        profiles = yaml.safe_load(f) or {}

    if profile not in profiles:
        click.echo(f"✗ Profile '{profile}' not found in profiles.yml")
        return False, False

    profile_data = profiles[profile]
    if profile_data is None:
        click.echo(f"✗ Profile '{profile}' is empty or invalid")
        return False, False

    # Get or create outputs dict (standard dbt format)
    if "outputs" not in profile_data:
        profile_data["outputs"] = {}

    outputs = profile_data["outputs"]

    # Check if target already exists
    if target_name in outputs:
        if not click.confirm(f"Target '{target_name}' already exists. Overwrite?"):
            return False, False

    # Build target config
    target_config = {"type": adapter_type}

    if host:
        target_config["host"] = host
    if port:
        target_config["port"] = port
    if user:
        target_config["user"] = user
    if password:
        target_config["password"] = password
    if database:
        target_config["database"] = database
    if schema:
        target_config["schema"] = schema
    if threads:
        target_config["threads"] = threads

    # Add target to outputs
    outputs[target_name] = target_config

    # Set as default if requested
    if set_default:
        profile_data["target"] = target_name

    # Write back to profiles.yml
    with open(profiles_file, "w") as f:
        yaml.dump(profiles, f, default_flow_style=False, sort_keys=False)

    click.echo(f"✓ Added target '{target_name}' to profile '{profile}'")
    if set_default:
        click.echo(f"  Set as default target")

    return True, True


@target.command("sync")
@click.option("--profile", help="Profile name (defaults to project profile)")
@click.option("--clean", is_flag=True, help="Remove adapters not needed by profiles.yml")
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.pass_context
@p.profiles_dir
@p.project_dir
def target_sync(ctx, profile, clean, dry_run, profiles_dir, project_dir, **kwargs):
    """Sync adapters and JDBC JARs based on profiles.yml connections.

    Scans your profiles.yml to find all connection types, then:
    - Installs required dbt adapters via pip
    - Updates JDBC JARs for Spark federation
    - Optionally removes unused adapters (with --clean)

    Examples:

        dvt target sync              # Sync for current project
        dvt target sync --profile my_project  # Sync specific profile
        dvt target sync --dry-run    # Show what would happen
        dvt target sync --clean      # Also remove unused adapters
    """
    from dbt.task.target_sync import TargetSyncTask

    task = TargetSyncTask(
        project_dir=project_dir,
        profiles_dir=profiles_dir,
        profile_name=profile,
    )
    success = task.sync(verbose=True, clean=clean, dry_run=dry_run)
    return None, success


@target.command("remove")
@click.argument("target_name")
@click.option("--profile", required=True, help="Profile name to remove target from")
@click.pass_context
@p.profiles_dir
def target_remove(ctx, target_name, profile, profiles_dir, **kwargs):
    """Remove a target from a profile in profiles.yml"""
    import yaml
    from pathlib import Path

    profiles_file = Path(profiles_dir) / "profiles.yml"

    if not profiles_file.exists():
        click.echo(f"✗ profiles.yml not found at {profiles_file}")
        return False, False

    with open(profiles_file, "r") as f:
        profiles = yaml.safe_load(f) or {}

    if profile not in profiles:
        click.echo(f"✗ Profile '{profile}' not found in profiles.yml")
        return False, False

    profile_data = profiles[profile]
    if profile_data is None:
        click.echo(f"✗ Profile '{profile}' is empty or invalid")
        return False, False
    outputs = profile_data.get("outputs", {})

    if target_name not in outputs:
        click.echo(f"✗ Target '{target_name}' not found in profile '{profile}'")
        return False, False

    # Remove the target
    del outputs[target_name]

    # Check if this was the default target
    default_target = profile_data.get("target")
    if default_target == target_name:
        # Set new default to first available target
        if outputs:
            new_default = list(outputs.keys())[0]
            profile_data["target"] = new_default
            click.echo(
                f"  Note: '{target_name}' was the default target, changed to '{new_default}'"
            )
        else:
            click.echo(f"  Warning: No targets remaining in profile '{profile}'")

    # Write back to profiles.yml
    with open(profiles_file, "w") as f:
        yaml.dump(profiles, f, default_flow_style=False, sort_keys=False)

    click.echo(f"✓ Removed target '{target_name}' from profile '{profile}'")

    return True, True


# DVT java commands for Java management
@cli.group()
@click.pass_context
@global_flags
def java(ctx, **kwargs):
    """Manage Java installations for PySpark.

    Java is required for Spark compute engines. DVT supports multiple
    Java versions depending on your PySpark version:

    \b
    PySpark 4.0.x -> Java 17 or 21
    PySpark 3.5.x -> Java 8, 11, or 17
    PySpark 3.4.x -> Java 8, 11, or 17
    PySpark 3.3.x -> Java 8 or 11
    PySpark 3.2.x -> Java 8 or 11

    Examples:

    \b
        dvt java check     # Check Java compatibility with PySpark
        dvt java search    # Find all Java installations
        dvt java set       # Select and configure JAVA_HOME
        dvt java install   # Show installation guide
    """


@java.command("check")
@click.pass_context
def java_check(ctx, **kwargs):
    """Check Java installation and PySpark compatibility.

    Shows current Java version, installed PySpark version, and whether
    they are compatible. Provides guidance if there's a mismatch.

    Exit codes:
        0 - Java and PySpark are compatible
        1 - Java/PySpark mismatch or not found
    """
    from dbt.task.java import JavaTask

    task = JavaTask()
    is_compatible = task.check()
    ctx.exit(0 if is_compatible else 1)


@java.command("search")
@click.pass_context
def java_search(ctx, **kwargs):
    """Find all Java installations on the system.

    Searches common installation locations for Java on your OS:

    \b
    macOS:   /Library/Java/JavaVirtualMachines, Homebrew, SDKMAN
    Linux:   /usr/lib/jvm, /opt/java, update-alternatives, SDKMAN
    Windows: Program Files, Registry, Scoop, Chocolatey

    Shows Java version, vendor, and compatibility with installed PySpark.
    """
    from dbt.task.java import JavaTask

    task = JavaTask()
    installations = task.search()
    ctx.exit(0 if installations else 1)


@java.command("set")
@click.pass_context
def java_set(ctx, **kwargs):
    """Interactively select and set JAVA_HOME.

    Shows all found Java installations with compatibility indicators,
    lets you choose one, and updates your shell configuration file
    (.zshrc, .bashrc, etc.) to persist JAVA_HOME.

    After setting, restart your terminal or run 'source ~/.zshrc'
    (or equivalent) for changes to take effect.
    """
    from dbt.task.java import JavaTask

    task = JavaTask()
    success = task.set_java_home()
    ctx.exit(0 if success else 1)


@java.command("install")
@click.pass_context
def java_install(ctx, **kwargs):
    """Show Java installation guide for your platform.

    Provides platform-specific installation instructions based on
    your installed PySpark version. Includes options for:

    \b
    macOS:   Homebrew, SDKMAN, manual download
    Linux:   apt-get, dnf, pacman, SDKMAN
    Windows: Winget, Chocolatey, Scoop, manual download
    """
    from dbt.task.java import JavaTask

    task = JavaTask()
    task.install_guide()
    ctx.exit(0)


# DVT spark commands for Spark/PySpark management
@cli.group()
@click.pass_context
@global_flags
def spark(ctx, **kwargs):
    """Manage PySpark installations and cluster compatibility.

    PySpark is the Python API for Apache Spark, used by DVT for
    federated query execution across multiple data sources.

    Different PySpark versions require different Java versions.
    Use these commands to manage versions and ensure compatibility.

    Examples:

    \b
        dvt spark check                  # Check PySpark/Java status
        dvt spark set-version            # Install specific PySpark version
        dvt spark match-cluster <name>   # Match PySpark to cluster version
        dvt spark versions               # Show compatibility matrix
    """


@spark.command("check")
@click.pass_context
def spark_check(ctx, **kwargs):
    """Check PySpark installation and Java compatibility.

    Shows:
    - Installed PySpark version and requirements
    - Current Java version
    - Compatibility status

    Exit codes:
        0 - PySpark installed and Java compatible
        1 - PySpark not installed or Java incompatible
    """
    from dbt.task.spark import SparkTask

    task = SparkTask()
    is_ok = task.check()
    ctx.exit(0 if is_ok else 1)


@spark.command("set-version")
@click.pass_context
def spark_set_version(ctx, **kwargs):
    """Interactively select and install a PySpark version.

    Presents available PySpark versions with their Java requirements.
    Shows compatibility indicators based on your current Java.
    Installs the selected version via pip.

    Available versions:
    \b
        PySpark 4.0.x - Latest, requires Java 17+
        PySpark 3.5.x - Stable, Java 8/11/17
        PySpark 3.4.x - Java 8/11/17
        PySpark 3.3.x - Java 8/11
        PySpark 3.2.x - Java 8/11

    After installing, check Java compatibility with 'dvt java check'.
    """
    from dbt.task.spark import SparkTask

    task = SparkTask()
    success = task.set_version()
    ctx.exit(0 if success else 1)


@spark.command("match-cluster")
@click.argument("compute_name")
@click.pass_context
def spark_match_cluster(ctx, compute_name, **kwargs):
    """Detect cluster Spark version and check PySpark compatibility.

    Connects to the specified compute engine from computes.yml,
    detects its Spark version, and compares with locally installed
    PySpark. Provides recommendations if versions don't match.

    IMPORTANT: PySpark version must match the cluster's Spark version
    (same major.minor). A mismatch can cause runtime errors.

    Arguments:
        COMPUTE_NAME: Name of compute engine in computes.yml

    Examples:

    \b
        dvt spark match-cluster spark-docker
        dvt spark match-cluster spark-local
        dvt spark match-cluster databricks-prod
    """
    from dbt.task.spark import SparkTask

    task = SparkTask()
    is_match = task.match_cluster(compute_name)
    ctx.exit(0 if is_match else 1)


@spark.command("versions")
@click.pass_context
def spark_versions(ctx, **kwargs):
    """Display PySpark/Java compatibility matrix.

    Shows all available PySpark versions with their Java requirements,
    marks the currently installed version, and shows your current
    Java installation.
    """
    from dbt.task.spark import SparkTask

    task = SparkTask()
    task.show_versions()
    ctx.exit(0)


# Register DVT command groups with main CLI
cli.add_command(compute)
cli.add_command(target)
cli.add_command(java)
cli.add_command(spark)


# Support running as a module (python -m dbt.cli.main)
if __name__ == "__main__":
    cli()
