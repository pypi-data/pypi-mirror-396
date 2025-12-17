# =============================================================================
# DVT Project Metadata Store
# =============================================================================
# DuckDB-based metadata store for DVT projects.
#
# This store contains PROJECT-LEVEL data only:
# - Column metadata (from dvt snap or federated runs)
# - Row counts (from dvt snap only, NOT during every run)
#
# Static registry data (type mappings, syntax rules, adapter queries) comes
# from the shipped adapters_registry.duckdb via AdaptersRegistry class.
#
# Location: <project>/.dvt/metadata_store.duckdb
#
# DVT v0.54.0: Initial implementation
# DVT v0.55.0: Refactored to separate project metadata from shipped registry
# =============================================================================

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    HAS_DUCKDB = False

from dbt.compute.metadata.adapters_registry import (
    AdaptersRegistry,
    TypeMapping,
    SyntaxRule,
    get_registry,
    get_spark_type as registry_get_spark_type,
    get_syntax_rule as registry_get_syntax_rule,
    get_metadata_query as registry_get_metadata_query,
)


@dataclass
class ColumnMetadata:
    """Metadata for a single column."""
    column_name: str
    adapter_type: str
    spark_type: str
    is_nullable: bool
    is_primary_key: bool
    ordinal_position: int


@dataclass
class TableMetadata:
    """Metadata for a table/view (columns only, no row count)."""
    source_name: str
    table_name: str
    adapter_name: str
    connection_name: str
    schema_name: str
    columns: List[ColumnMetadata]
    last_refreshed: datetime


@dataclass
class RowCountInfo:
    """Row count information for a table."""
    source_name: str
    table_name: str
    row_count: int
    last_refreshed: datetime


class ProjectMetadataStore:
    """
    DuckDB-based metadata store for a DVT project.

    Location: <project_root>/.dvt/metadata_store.duckdb

    Tables (project-level data only):
    - column_metadata: source_name, table_name, column_name, adapter_type, spark_type, ...
    - row_counts: source_name, table_name, row_count, last_refreshed

    NOTE: Static registry data (type mappings, syntax rules, adapter queries)
    comes from the shipped adapters_registry.duckdb via AdaptersRegistry class.
    """

    DVT_DIR = ".dvt"
    METADATA_DB = "metadata_store.duckdb"

    def __init__(self, project_root: Path):
        """
        Initialize the metadata store.

        Args:
            project_root: Path to the DVT project root directory
        """
        if not HAS_DUCKDB:
            raise ImportError(
                "DuckDB is required for metadata store. "
                "Install with: pip install duckdb"
            )

        self.project_root = Path(project_root)
        self.dvt_dir = self.project_root / self.DVT_DIR
        self.db_path = self.dvt_dir / self.METADATA_DB
        self._conn: Optional[duckdb.DuckDBPyConnection] = None
        self._registry: Optional[AdaptersRegistry] = None

    @property
    def conn(self) -> "duckdb.DuckDBPyConnection":
        """Get or create database connection."""
        if self._conn is None:
            self._conn = duckdb.connect(str(self.db_path))
        return self._conn

    @property
    def registry(self) -> AdaptersRegistry:
        """Get the shipped adapters registry (singleton)."""
        if self._registry is None:
            self._registry = get_registry()
        return self._registry

    def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "ProjectMetadataStore":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    # =========================================================================
    # Initialization
    # =========================================================================

    def initialize(self) -> None:
        """
        Initialize the metadata store.

        Creates:
        1. .dvt/ directory if it doesn't exist
        2. metadata_store.duckdb database
        3. Schema tables (column_metadata, row_counts)

        NOTE: No registry data is loaded - that comes from shipped DuckDB.
        """
        # Create .dvt/ directory
        self.dvt_dir.mkdir(parents=True, exist_ok=True)

        # Create schema tables
        self._create_schema()

    def _create_schema(self) -> None:
        """Create the database schema tables."""

        # Column metadata table (populated by dvt snap or federated runs)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS column_metadata (
                source_name VARCHAR NOT NULL,
                table_name VARCHAR NOT NULL,
                column_name VARCHAR NOT NULL,
                adapter_name VARCHAR NOT NULL,
                connection_name VARCHAR NOT NULL,
                schema_name VARCHAR,
                adapter_type VARCHAR NOT NULL,
                spark_type VARCHAR NOT NULL,
                is_nullable BOOLEAN DEFAULT TRUE,
                is_primary_key BOOLEAN DEFAULT FALSE,
                ordinal_position INTEGER,
                last_refreshed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(source_name, table_name, column_name)
            )
        """)

        # Row counts table (ONLY populated by dvt snap, not during runs)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS row_counts (
                source_name VARCHAR NOT NULL,
                table_name VARCHAR NOT NULL,
                row_count BIGINT,
                last_refreshed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(source_name, table_name)
            )
        """)

        # Create indexes for fast lookups
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_column_metadata_source
            ON column_metadata(source_name, table_name)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_column_metadata_adapter
            ON column_metadata(adapter_name)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_row_counts_source
            ON row_counts(source_name)
        """)

    # =========================================================================
    # Type Registry Queries (delegated to shipped AdaptersRegistry)
    # =========================================================================

    def get_spark_type(
        self,
        adapter_name: str,
        adapter_type: str,
        spark_version: str = "all"
    ) -> Optional[str]:
        """
        Look up the Spark type for an adapter type.

        Delegates to the shipped AdaptersRegistry.

        Args:
            adapter_name: Name of the adapter (e.g., 'postgres', 'snowflake')
            adapter_type: Native adapter type (e.g., 'VARCHAR', 'INTEGER')
            spark_version: Target Spark version (default: 'all')

        Returns:
            Spark type string or None if not found
        """
        mapping = self.registry.get_spark_type(adapter_name, adapter_type, spark_version)
        return mapping.spark_type if mapping else None

    def get_type_mappings(
        self,
        adapter_name: str,
        spark_version: str = "all"
    ) -> List[Tuple[str, str]]:
        """
        Get all type mappings for an adapter.

        Delegates to the shipped AdaptersRegistry.

        Returns:
            List of (adapter_type, spark_type) tuples
        """
        mappings = self.registry.get_all_mappings_for_adapter(adapter_name)
        return [(m.adapter_type, m.spark_type) for m in mappings]

    # =========================================================================
    # Syntax Registry Queries (delegated to shipped AdaptersRegistry)
    # =========================================================================

    def get_syntax_rule(self, adapter_name: str) -> Optional[SyntaxRule]:
        """
        Get syntax rules for an adapter.

        Delegates to the shipped AdaptersRegistry.

        Args:
            adapter_name: Name of the adapter

        Returns:
            SyntaxRule or None if not found
        """
        return self.registry.get_syntax_rule(adapter_name)

    def quote_identifier(self, adapter_name: str, identifier: str) -> str:
        """Quote an identifier for the given adapter."""
        return self.registry.quote_identifier(adapter_name, identifier)

    # =========================================================================
    # Adapter Metadata Queries (delegated to shipped AdaptersRegistry)
    # =========================================================================

    def get_metadata_query(
        self,
        adapter_name: str,
        query_type: str
    ) -> Optional[str]:
        """
        Get the metadata query template for an adapter.

        Delegates to the shipped AdaptersRegistry.

        Args:
            adapter_name: Name of the adapter
            query_type: Type of query ('columns', 'tables', 'row_count', 'primary_key')

        Returns:
            Query template string or None if not found
        """
        query = self.registry.get_metadata_query(adapter_name, query_type)
        return query.query_template if query else None

    # =========================================================================
    # Column Metadata Operations
    # =========================================================================

    def save_table_metadata(self, metadata: TableMetadata) -> None:
        """
        Save table column metadata to the store.

        This is called during federated execution to capture schema info.

        Args:
            metadata: TableMetadata object with column info
        """
        # Delete existing entries for this table
        self.conn.execute("""
            DELETE FROM column_metadata
            WHERE source_name = ? AND table_name = ?
        """, [metadata.source_name, metadata.table_name])

        # Insert new entries
        for col in metadata.columns:
            self.conn.execute("""
                INSERT INTO column_metadata
                (source_name, table_name, column_name, adapter_name, connection_name,
                 schema_name, adapter_type, spark_type, is_nullable, is_primary_key,
                 ordinal_position, last_refreshed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                metadata.source_name,
                metadata.table_name,
                col.column_name,
                metadata.adapter_name,
                metadata.connection_name,
                metadata.schema_name,
                col.adapter_type,
                col.spark_type,
                col.is_nullable,
                col.is_primary_key,
                col.ordinal_position,
                metadata.last_refreshed
            ])

    def get_table_metadata(
        self,
        source_name: str,
        table_name: str
    ) -> Optional[TableMetadata]:
        """
        Get cached column metadata for a table.

        Args:
            source_name: Name of the source
            table_name: Name of the table

        Returns:
            TableMetadata or None if not cached
        """
        results = self.conn.execute("""
            SELECT
                source_name, table_name, column_name, adapter_name, connection_name,
                schema_name, adapter_type, spark_type, is_nullable, is_primary_key,
                ordinal_position, last_refreshed
            FROM column_metadata
            WHERE source_name = ? AND table_name = ?
            ORDER BY ordinal_position
        """, [source_name, table_name]).fetchall()

        if not results:
            return None

        # Build column list
        columns = []
        for r in results:
            columns.append(ColumnMetadata(
                column_name=r[2],
                adapter_type=r[6],
                spark_type=r[7],
                is_nullable=r[8],
                is_primary_key=r[9],
                ordinal_position=r[10]
            ))

        # Build TableMetadata from first row
        first = results[0]
        return TableMetadata(
            source_name=first[0],
            table_name=first[1],
            adapter_name=first[3],
            connection_name=first[4],
            schema_name=first[5],
            columns=columns,
            last_refreshed=first[11]
        )

    def get_all_sources(self) -> List[Tuple[str, str]]:
        """
        Get all source/table combinations in the store.

        Returns:
            List of (source_name, table_name) tuples
        """
        results = self.conn.execute("""
            SELECT DISTINCT source_name, table_name
            FROM column_metadata
            ORDER BY source_name, table_name
        """).fetchall()

        return [(r[0], r[1]) for r in results]

    def clear_column_metadata(self) -> None:
        """Clear all column metadata."""
        self.conn.execute("DELETE FROM column_metadata")

    # =========================================================================
    # Row Count Operations (dvt snap only)
    # =========================================================================

    def save_row_count(
        self,
        source_name: str,
        table_name: str,
        row_count: int,
        last_refreshed: Optional[datetime] = None
    ) -> None:
        """
        Save row count for a table.

        This is ONLY called by dvt snap, not during regular runs.

        Args:
            source_name: Name of the source
            table_name: Name of the table
            row_count: Number of rows
            last_refreshed: Timestamp (defaults to now)
        """
        if last_refreshed is None:
            last_refreshed = datetime.now()

        self.conn.execute("""
            INSERT OR REPLACE INTO row_counts
            (source_name, table_name, row_count, last_refreshed)
            VALUES (?, ?, ?, ?)
        """, [source_name, table_name, row_count, last_refreshed])

    def get_row_count(self, source_name: str, table_name: str) -> Optional[RowCountInfo]:
        """
        Get cached row count for a table.

        Args:
            source_name: Name of the source
            table_name: Name of the table

        Returns:
            RowCountInfo or None if not cached
        """
        result = self.conn.execute("""
            SELECT source_name, table_name, row_count, last_refreshed
            FROM row_counts
            WHERE source_name = ? AND table_name = ?
        """, [source_name, table_name]).fetchone()

        if result:
            return RowCountInfo(
                source_name=result[0],
                table_name=result[1],
                row_count=result[2],
                last_refreshed=result[3]
            )
        return None

    def get_all_row_counts(self) -> List[RowCountInfo]:
        """
        Get all cached row counts.

        Returns:
            List of RowCountInfo objects
        """
        results = self.conn.execute("""
            SELECT source_name, table_name, row_count, last_refreshed
            FROM row_counts
            ORDER BY source_name, table_name
        """).fetchall()

        return [
            RowCountInfo(
                source_name=r[0],
                table_name=r[1],
                row_count=r[2],
                last_refreshed=r[3]
            )
            for r in results
        ]

    def clear_row_counts(self) -> None:
        """Clear all row count data."""
        self.conn.execute("DELETE FROM row_counts")

    def clear_snapshot(self) -> None:
        """Clear all snapshot data (both column metadata and row counts)."""
        self.clear_column_metadata()
        self.clear_row_counts()

    # =========================================================================
    # Legacy Compatibility - save_table_metadata with row_count
    # =========================================================================

    def save_table_metadata_with_row_count(
        self,
        source_name: str,
        table_name: str,
        adapter_name: str,
        connection_name: str,
        schema_name: str,
        columns: List[ColumnMetadata],
        row_count: Optional[int],
        last_refreshed: datetime
    ) -> None:
        """
        Save both column metadata and row count (used by dvt snap).

        Args:
            source_name: Name of the source
            table_name: Name of the table
            adapter_name: Name of the adapter
            connection_name: Name of the connection
            schema_name: Schema name
            columns: List of ColumnMetadata
            row_count: Number of rows (or None)
            last_refreshed: Timestamp
        """
        # Save column metadata
        metadata = TableMetadata(
            source_name=source_name,
            table_name=table_name,
            adapter_name=adapter_name,
            connection_name=connection_name,
            schema_name=schema_name,
            columns=columns,
            last_refreshed=last_refreshed
        )
        self.save_table_metadata(metadata)

        # Save row count separately (only if provided)
        if row_count is not None:
            self.save_row_count(source_name, table_name, row_count, last_refreshed)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def exists(self) -> bool:
        """Check if the metadata store exists."""
        return self.db_path.exists()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the metadata store."""
        # Count column metadata
        tables_count = self.conn.execute(
            "SELECT COUNT(DISTINCT source_name || '.' || table_name) FROM column_metadata"
        ).fetchone()[0]

        columns_count = self.conn.execute(
            "SELECT COUNT(*) FROM column_metadata"
        ).fetchone()[0]

        # Count row counts
        row_counts_count = self.conn.execute(
            "SELECT COUNT(*) FROM row_counts"
        ).fetchone()[0]

        # Get registry stats
        registry = self.registry
        adapters = registry.get_supported_adapters()

        return {
            "metadata_tables": tables_count,
            "metadata_columns": columns_count,
            "row_counts_cached": row_counts_count,
            "registry_adapters": len(adapters),
            "supported_adapters": adapters,
            "db_path": str(self.db_path),
        }

    def migrate_from_legacy(self) -> bool:
        """
        Migrate from legacy metadata.duckdb format to new format.

        Returns:
            True if migration was performed, False if not needed
        """
        legacy_path = self.dvt_dir / "metadata.duckdb"
        if not legacy_path.exists():
            return False

        # Check if new store already exists
        if self.db_path.exists():
            return False

        try:
            # Connect to legacy database
            legacy_conn = duckdb.connect(str(legacy_path), read_only=True)

            # Check if metadata_snapshot table exists
            result = legacy_conn.execute("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = 'metadata_snapshot'
            """).fetchone()[0]

            if result == 0:
                legacy_conn.close()
                return False

            # Initialize new store
            self.initialize()

            # Migrate metadata_snapshot to column_metadata
            rows = legacy_conn.execute("""
                SELECT DISTINCT
                    source_name, table_name, column_name, adapter_name, connection_name,
                    schema_name, adapter_type, spark_type, is_nullable, is_primary_key,
                    ordinal_position, last_refreshed
                FROM metadata_snapshot
            """).fetchall()

            for row in rows:
                self.conn.execute("""
                    INSERT OR REPLACE INTO column_metadata
                    (source_name, table_name, column_name, adapter_name, connection_name,
                     schema_name, adapter_type, spark_type, is_nullable, is_primary_key,
                     ordinal_position, last_refreshed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, list(row))

            # Migrate row_count data (distinct per table)
            row_count_rows = legacy_conn.execute("""
                SELECT DISTINCT source_name, table_name, row_count, MAX(last_refreshed)
                FROM metadata_snapshot
                WHERE row_count IS NOT NULL
                GROUP BY source_name, table_name, row_count
            """).fetchall()

            for row in row_count_rows:
                if row[2] is not None:  # row_count
                    self.conn.execute("""
                        INSERT OR REPLACE INTO row_counts
                        (source_name, table_name, row_count, last_refreshed)
                        VALUES (?, ?, ?, ?)
                    """, list(row))

            legacy_conn.close()
            return True

        except Exception as e:
            print(f"[DVT] Warning: Migration failed: {e}")
            return False
