# =============================================================================
# DVT Snap Task
# =============================================================================
# Captures metadata snapshots from source databases.
#
# Usage:
#   dvt snap                  # Snapshot all sources
#   dvt snap --source <name>  # Snapshot specific source
#   dvt snap --all            # Snapshot sources + models (Phase 2.2)
#
# DVT v0.54.0: Initial implementation
# =============================================================================

import click
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from dbt.task.base import BaseTask
from dbt.flags import get_flags


class SnapTask(BaseTask):
    """
    Task to capture metadata snapshots from source databases.

    This task:
    1. Reads source definitions from the project
    2. Connects to each source database via the adapter
    3. Fetches table/column metadata
    4. Maps adapter types to Spark types
    5. Stores metadata in .dvt/metadata.duckdb
    """

    def __init__(self, args):
        super().__init__(args)
        self._metadata_store = None

    @property
    def metadata_store(self):
        """Lazy load the metadata store."""
        if self._metadata_store is None:
            from dbt.compute.metadata import ProjectMetadataStore
            project_root = Path(get_flags().PROJECT_DIR or ".")
            self._metadata_store = ProjectMetadataStore(project_root)
        return self._metadata_store

    def run(self):
        """Execute the snap task."""
        from dbt.compute.metadata import ProjectMetadataStore
        from dbt.compute.metadata.store import TableMetadata, ColumnMetadata
        from dbt.compute.metadata.registry import TypeRegistry

        # Get project root from args or use current directory
        project_dir = getattr(self.args, 'project_dir', None)
        project_root = Path(project_dir) if project_dir else Path(".")

        # Check if metadata store exists (v0.55.0: renamed to metadata_store.duckdb)
        if not (project_root / ".dvt" / "metadata_store.duckdb").exists():
            click.echo(click.style(
                "Metadata store not initialized. Run 'dvt init' first.",
                fg="red"
            ))
            return False, False

        # Get source name filter if provided
        source_filter = getattr(self.args, 'source', None)
        include_all = getattr(self.args, 'all', False)

        click.echo(click.style("DVT Snap - Capturing Metadata Snapshot", fg="cyan", bold=True))
        click.echo("")

        # Load sources from project
        sources = self._load_sources(project_root)

        if not sources:
            click.echo(click.style("No sources found in project.", fg="yellow"))
            return True, True

        # Filter sources if requested
        if source_filter:
            sources = {k: v for k, v in sources.items() if k == source_filter}
            if not sources:
                click.echo(click.style(f"Source '{source_filter}' not found.", fg="red"))
                return False, False

        click.echo(f"Found {len(sources)} source(s) to snapshot")
        click.echo("")

        # Open metadata store
        with ProjectMetadataStore(project_root) as store:
            total_tables = 0
            total_columns = 0
            errors = []

            for source_name, source_config in sources.items():
                click.echo(f"Snapping source: {click.style(source_name, fg='cyan')}")

                try:
                    tables_count, columns_count = self._snap_source(
                        store, source_name, source_config
                    )
                    total_tables += tables_count
                    total_columns += columns_count
                    click.echo(f"  {click.style('OK', fg='green')} - {tables_count} tables, {columns_count} columns")
                except Exception as e:
                    errors.append((source_name, str(e)))
                    click.echo(f"  {click.style('FAILED', fg='red')} - {e}")

        # Phase 2.2: If --all, also snapshot models
        model_tables = 0
        model_columns = 0
        if include_all:
            click.echo("")
            click.echo(click.style("Snapping models...", fg="cyan"))

            models = self._load_models(project_root)
            if models:
                click.echo(f"Found {len(models)} model(s) to snapshot")

                with ProjectMetadataStore(project_root) as store:
                    for model_name, model_config in models.items():
                        try:
                            m_tables, m_cols = self._snap_model(
                                store, model_name, model_config
                            )
                            model_tables += m_tables
                            model_columns += m_cols
                            if m_tables > 0:
                                click.echo(f"  {click.style('OK', fg='green')} - {model_name}: {m_cols} columns")
                        except Exception as e:
                            errors.append((f"model:{model_name}", str(e)))
                            click.echo(f"  {click.style('FAILED', fg='red')} - {model_name}: {e}")
            else:
                click.echo(click.style("No models with column definitions found.", fg="yellow"))

            total_tables += model_tables
            total_columns += model_columns

        # Summary
        click.echo("")
        click.echo("=" * 60)
        if errors:
            click.echo(click.style(
                f"Completed with {len(errors)} error(s): {total_tables} tables, {total_columns} columns",
                fg="yellow"
            ))
        else:
            summary = f"Success: {total_tables} tables, {total_columns} columns captured"
            if include_all and model_tables > 0:
                summary += f" (including {model_tables} models)"
            click.echo(click.style(summary, fg="green"))

        return len(errors) == 0, True

    def _load_sources(self, project_root: Path) -> Dict[str, Dict[str, Any]]:
        """
        Load source definitions from the project.

        Returns:
            Dict mapping source_name -> source configuration
        """
        import yaml

        sources = {}

        # Look for sources.yml files in models/ directory
        models_dir = project_root / "models"
        if not models_dir.exists():
            return sources

        # Find all sources.yml files
        for yml_file in models_dir.rglob("*.yml"):
            try:
                with open(yml_file) as f:
                    content = yaml.safe_load(f)

                if content and "sources" in content:
                    for source in content["sources"]:
                        source_name = source.get("name")
                        if source_name:
                            sources[source_name] = source
            except Exception:
                pass  # Skip files that can't be parsed

        return sources

    def _load_models(self, project_root: Path) -> Dict[str, Dict[str, Any]]:
        """
        Load model definitions from the project.

        Looks for models with column definitions in schema.yml files.

        Returns:
            Dict mapping model_name -> model configuration
        """
        import yaml

        models = {}

        # Look for schema.yml files in models/ directory
        models_dir = project_root / "models"
        if not models_dir.exists():
            return models

        # Find all yml files that might contain model definitions
        for yml_file in models_dir.rglob("*.yml"):
            try:
                with open(yml_file) as f:
                    content = yaml.safe_load(f)

                if content and "models" in content:
                    for model in content["models"]:
                        model_name = model.get("name")
                        if model_name and model.get("columns"):
                            # Store model config with file path for context
                            model["_file_path"] = str(yml_file)
                            models[model_name] = model
            except Exception:
                pass  # Skip files that can't be parsed

        return models

    def _snap_model(
        self,
        store,
        model_name: str,
        model_config: Dict[str, Any]
    ) -> Tuple[int, int]:
        """
        Snapshot metadata from a model definition.

        Args:
            store: ProjectMetadataStore instance
            model_name: Name of the model
            model_config: Model configuration from schema.yml

        Returns:
            Tuple of (tables_count, columns_count)
        """
        from dbt.compute.metadata.store import TableMetadata, ColumnMetadata
        from dbt.compute.metadata.registry import TypeRegistry

        columns_config = model_config.get("columns", [])
        if not columns_config:
            return 0, 0

        # Get target adapter from model config or use default
        # Models can specify target via config block
        config = model_config.get("config", {})
        target_name = config.get("target", "default")
        materialization = config.get("materialized", "view")

        # Infer adapter type - would normally come from profile
        # For now, use 'databricks' as default target adapter (common for DVT)
        adapter_name = config.get("adapter_type", "databricks")

        # Build column metadata
        columns = []
        for idx, col_config in enumerate(columns_config):
            col_name = col_config.get("name")
            if not col_name:
                continue

            # Get the data type - models often define this in tests or config
            adapter_type = col_config.get("data_type", "STRING")

            # Look up Spark type
            type_info = TypeRegistry.get_spark_type(adapter_name, adapter_type)
            spark_type = type_info["spark_native_type"] if type_info else "StringType"

            # Check for not_null test to infer nullability
            is_nullable = True
            tests = col_config.get("tests", []) or col_config.get("data_tests", [])
            if tests:
                for test in tests:
                    if test == "not_null" or (isinstance(test, dict) and "not_null" in test):
                        is_nullable = False
                        break

            # Check for unique/primary key
            is_primary_key = False
            if tests:
                for test in tests:
                    if test == "unique" or (isinstance(test, dict) and "unique" in test):
                        is_primary_key = True
                        break

            columns.append(ColumnMetadata(
                column_name=col_name,
                adapter_type=adapter_type,
                spark_type=spark_type,
                is_nullable=is_nullable,
                is_primary_key=is_primary_key,
                ordinal_position=idx + 1,
            ))

        if columns:
            # Create table metadata with "model:" prefix for source_name
            metadata = TableMetadata(
                source_name=f"model:{model_name}",
                table_name=model_name,
                adapter_name=adapter_name,
                connection_name=target_name,
                schema_name=config.get("schema", "default"),
                columns=columns,
                last_refreshed=datetime.now(),
            )

            # Save to store
            store.save_table_metadata(metadata)

            return 1, len(columns)

        return 0, 0

    def _snap_source(
        self,
        store,
        source_name: str,
        source_config: Dict[str, Any]
    ) -> Tuple[int, int]:
        """
        Snapshot metadata from a single source.

        Args:
            store: ProjectMetadataStore instance
            source_name: Name of the source
            source_config: Source configuration from sources.yml

        Returns:
            Tuple of (tables_count, columns_count)
        """
        from dbt.compute.metadata.store import TableMetadata, ColumnMetadata
        from dbt.compute.metadata.registry import TypeRegistry

        tables_count = 0
        columns_count = 0

        # Get connection info from source config
        database = source_config.get("database")
        schema = source_config.get("schema", "public")
        tables = source_config.get("tables", [])

        # Get the adapter type from the connection
        # This would normally come from the profile, but for now we'll
        # try to infer it or use a default
        adapter_name = source_config.get("adapter", "postgres")

        for table_config in tables:
            table_name = table_config.get("name")
            if not table_name:
                continue

            # For now, we create synthetic metadata based on source definition
            # In a real implementation, this would query the actual database
            columns_config = table_config.get("columns", [])

            if not columns_config:
                # No columns defined - we'd need to query the database
                # For now, skip tables without column definitions
                continue

            # Build column metadata
            columns = []
            for idx, col_config in enumerate(columns_config):
                col_name = col_config.get("name")
                if not col_name:
                    continue

                # Get the adapter type (may be specified or inferred)
                adapter_type = col_config.get("data_type", "VARCHAR")

                # Look up Spark type
                type_info = TypeRegistry.get_spark_type(adapter_name, adapter_type)
                spark_type = type_info["spark_native_type"] if type_info else "StringType"

                columns.append(ColumnMetadata(
                    column_name=col_name,
                    adapter_type=adapter_type,
                    spark_type=spark_type,
                    is_nullable=col_config.get("nullable", True),
                    is_primary_key=col_config.get("primary_key", False),
                    ordinal_position=idx + 1,
                ))

            if columns:
                # Create table metadata
                metadata = TableMetadata(
                    source_name=source_name,
                    table_name=table_name,
                    adapter_name=adapter_name,
                    connection_name=source_name,  # Use source name as connection
                    schema_name=schema,
                    columns=columns,
                    last_refreshed=datetime.now(),
                )

                # Save to store
                store.save_table_metadata(metadata)

                tables_count += 1
                columns_count += len(columns)

        return tables_count, columns_count


class SnapLiveTask(SnapTask):
    """
    Task to capture live metadata from actual database connections.

    This version actually connects to databases and queries metadata.
    """

    def _snap_source_live(
        self,
        store,
        source_name: str,
        source_config: Dict[str, Any],
        adapter
    ) -> Tuple[int, int]:
        """
        Snapshot live metadata from a database connection.

        Args:
            store: ProjectMetadataStore instance
            source_name: Name of the source
            source_config: Source configuration
            adapter: Database adapter instance

        Returns:
            Tuple of (tables_count, columns_count)
        """
        from dbt.compute.metadata.store import TableMetadata, ColumnMetadata
        from dbt.compute.metadata.registry import TypeRegistry

        tables_count = 0
        columns_count = 0

        schema = source_config.get("schema", "public")
        tables = source_config.get("tables", [])
        adapter_name = adapter.type()

        # Get metadata query template
        columns_query = store.get_metadata_query(adapter_name, "columns")

        for table_config in tables:
            table_name = table_config.get("name")
            if not table_name:
                continue

            try:
                # Execute columns query
                query = columns_query.format(schema=schema, table=table_name)
                with adapter.connection_named('snap'):
                    _, cursor = adapter.execute(query, fetch=True)
                    rows = cursor.fetchall()

                # Build column metadata
                columns = []
                for row in rows:
                    col_name = row[0]
                    adapter_type = row[1]
                    is_nullable = row[2]
                    ordinal = row[3]

                    # Look up Spark type
                    type_info = TypeRegistry.get_spark_type(adapter_name, adapter_type)
                    spark_type = type_info["spark_native_type"] if type_info else "StringType"

                    columns.append(ColumnMetadata(
                        column_name=col_name,
                        adapter_type=adapter_type,
                        spark_type=spark_type,
                        is_nullable=is_nullable,
                        is_primary_key=False,  # Would need additional query
                        ordinal_position=ordinal,
                    ))

                # TODO: Store row count separately using RowCountInfo
                # Row counts are now stored in a separate table (row_counts)
                # This can be implemented when live snapping is fully supported

                if columns:
                    metadata = TableMetadata(
                        source_name=source_name,
                        table_name=table_name,
                        adapter_name=adapter_name,
                        connection_name=source_name,
                        schema_name=schema,
                        columns=columns,
                        last_refreshed=datetime.now(),
                    )

                    store.save_table_metadata(metadata)
                    tables_count += 1
                    columns_count += len(columns)

            except Exception as e:
                click.echo(f"    Warning: Could not snapshot table {table_name}: {e}")

        return tables_count, columns_count
