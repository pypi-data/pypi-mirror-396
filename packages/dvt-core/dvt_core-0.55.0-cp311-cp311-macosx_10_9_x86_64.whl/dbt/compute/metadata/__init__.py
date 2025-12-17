# =============================================================================
# DVT Metadata Layer
# =============================================================================
# Project-level metadata store using DuckDB for:
# - Type registry (adapter types → Spark types)
# - Syntax registry (quoting, case sensitivity per adapter)
# - Metadata snapshot (cached table/column info)
#
# DVT v0.54.0: Initial implementation
# DVT v0.55.0: Added AdaptersRegistry for shipped registry database
# =============================================================================

from dbt.compute.metadata.store import ProjectMetadataStore
from dbt.compute.metadata.registry import TypeRegistry, SyntaxRegistry
from dbt.compute.metadata.adapters_registry import AdaptersRegistry

__all__ = [
    "ProjectMetadataStore",
    "TypeRegistry",
    "SyntaxRegistry",
    "AdaptersRegistry",
]
