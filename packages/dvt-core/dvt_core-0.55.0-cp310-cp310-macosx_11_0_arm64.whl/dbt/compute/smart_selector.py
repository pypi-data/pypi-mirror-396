"""
Smart Compute Engine Selector

Automatically selects the optimal compute engine (Spark Local vs Spark Cluster) based on
workload characteristics when user doesn't specify a preference.

Selection criteria:
- Estimated data size
- Number of sources
- Query complexity
- Available resources
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.graph.nodes import ManifestNode
from dbt.query_analyzer import QueryAnalysisResult


@dataclass
class WorkloadEstimate:
    """Estimated workload characteristics for a query."""

    estimated_rows: int  # Estimated total rows to process
    source_count: int  # Number of source tables
    connection_count: int  # Number of different connections
    has_aggregations: bool  # Query contains GROUP BY or aggregations
    has_joins: bool  # Query contains JOIN operations
    complexity_score: float  # 0.0 to 1.0, higher = more complex

    @property
    def estimated_data_mb(self) -> float:
        """Rough estimate of data size in MB (assuming ~100 bytes/row)."""
        return (self.estimated_rows * 100) / (1024 * 1024)


class SmartComputeSelector:
    """
    Intelligently selects compute engine based on workload characteristics.

    v0.3.0: Unified Spark architecture - selects between spark-local and spark-cluster.

    Default thresholds:
    - Small/medium workload (<10GB): spark-local
    - Large workload (>10GB): spark-cluster (if configured)
    """

    # Default thresholds (can be configured)
    CLUSTER_THRESHOLD_MB = 10000  # 10GB - threshold for cluster recommendation
    CLUSTER_THRESHOLD_GB = 10  # Same in GB for clarity

    def __init__(
        self,
        manifest: Manifest,
        cluster_threshold_mb: Optional[int] = None,
        compute_registry: Optional[Any] = None,
    ):
        """
        Initialize smart selector.

        :param manifest: The dbt manifest
        :param cluster_threshold_mb: Data size threshold for cluster (default: 10GB)
        :param compute_registry: ComputeRegistry instance for checking cluster availability
        """
        self.manifest = manifest
        self.cluster_threshold_mb = cluster_threshold_mb or self.CLUSTER_THRESHOLD_MB
        self.compute_registry = compute_registry

    def select_engine(
        self, node: ManifestNode, analysis_result: QueryAnalysisResult
    ) -> str:
        """
        Select the optimal compute engine for a node.

        v0.3.0: Returns "spark-local" or "spark-cluster"

        :param node: The node to execute
        :param analysis_result: Query analysis result
        :returns: "spark-local" or "spark-cluster"
        """
        # Estimate workload
        estimate = self._estimate_workload(node, analysis_result)

        # Apply selection logic
        return self._apply_selection_logic(estimate)

    def _estimate_workload(
        self, node: ManifestNode, analysis_result: QueryAnalysisResult
    ) -> WorkloadEstimate:
        """
        Estimate workload characteristics for a node.

        :param node: The node to analyze
        :param analysis_result: Query analysis result
        :returns: WorkloadEstimate
        """
        # Count sources
        source_count = len(analysis_result.source_refs)
        connection_count = len(analysis_result.source_connections)

        # Estimate row count from sources
        estimated_rows = self._estimate_row_count(analysis_result.source_refs)

        # Analyze SQL for complexity
        sql = node.compiled_code if hasattr(node, "compiled_code") else node.raw_code
        has_aggregations = self._has_aggregations(sql)
        has_joins = self._has_joins(sql)

        # Calculate complexity score
        complexity_score = self._calculate_complexity(
            source_count=source_count,
            connection_count=connection_count,
            has_aggregations=has_aggregations,
            has_joins=has_joins,
        )

        return WorkloadEstimate(
            estimated_rows=estimated_rows,
            source_count=source_count,
            connection_count=connection_count,
            has_aggregations=has_aggregations,
            has_joins=has_joins,
            complexity_score=complexity_score,
        )

    def _estimate_row_count(self, source_refs: set) -> int:
        """
        Estimate total row count from source tables.

        Uses catalog metadata if available, otherwise uses heuristics.

        :param source_refs: Set of source unique_ids
        :returns: Estimated row count
        """
        total_rows = 0

        for source_id in source_refs:
            source = self.manifest.sources.get(source_id)
            if not source:
                # Unknown source, use conservative estimate
                total_rows += 100000
                continue

            # Check if we have catalog metadata with row counts
            # Note: This would come from `dbt docs generate`
            # For now, use a heuristic based on naming
            if (
                "fact" in source.identifier.lower()
                or "events" in source.identifier.lower()
            ):
                # Fact tables tend to be larger
                total_rows += 1000000
            elif (
                "dim" in source.identifier.lower()
                or "lookup" in source.identifier.lower()
            ):
                # Dimension tables tend to be smaller
                total_rows += 10000
            else:
                # Default estimate
                total_rows += 100000

        return total_rows

    def _has_aggregations(self, sql: str) -> bool:
        """Check if SQL contains aggregations."""
        sql_upper = sql.upper()
        return any(
            keyword in sql_upper
            for keyword in [
                " GROUP BY ",
                " SUM(",
                " COUNT(",
                " AVG(",
                " MIN(",
                " MAX(",
                " HAVING ",
            ]
        )

    def _has_joins(self, sql: str) -> bool:
        """Check if SQL contains joins."""
        sql_upper = sql.upper()
        return any(
            keyword in sql_upper
            for keyword in [
                " JOIN ",
                " INNER JOIN ",
                " LEFT JOIN ",
                " RIGHT JOIN ",
                " FULL JOIN ",
                " CROSS JOIN ",
            ]
        )

    def _calculate_complexity(
        self,
        source_count: int,
        connection_count: int,
        has_aggregations: bool,
        has_joins: bool,
    ) -> float:
        """
        Calculate query complexity score (0.0 to 1.0).

        :returns: Complexity score
        """
        score = 0.0

        # Source count contributes
        score += min(source_count / 10.0, 0.3)

        # Multiple connections increases complexity
        score += min(connection_count / 5.0, 0.2)

        # Aggregations add complexity
        if has_aggregations:
            score += 0.2

        # Joins add complexity
        if has_joins:
            score += 0.3

        return min(score, 1.0)

    def _apply_selection_logic(self, estimate: WorkloadEstimate) -> str:
        """
        Apply selection logic based on workload estimate.

        v0.3.0: Selects between spark-local and spark-cluster only.

        :param estimate: WorkloadEstimate
        :returns: "spark-local" or "spark-cluster"
        """
        # Rule 1: Large data → prefer cluster (if available)
        if estimate.estimated_data_mb > self.cluster_threshold_mb:
            # Check if cluster is configured
            if self._cluster_available():
                return "spark-cluster"
            else:
                # Log warning about large data on local
                # Note: Logging should be done by caller, we just return the engine
                return "spark-local"

        # Rule 2: Everything else → spark-local (default)
        # spark-local is excellent for most workloads (<10GB)
        return "spark-local"

    def _cluster_available(self) -> bool:
        """
        Check if a Spark cluster is configured.

        :returns: True if cluster compute engine is available
        """
        if not self.compute_registry:
            return False

        # Check if any cluster computes are registered (not spark-local)
        clusters = self.compute_registry.list()
        for cluster in clusters:
            if cluster.type == "spark" and cluster.name != "spark-local":
                # Check if it's actually a cluster (not local master)
                config = cluster.config
                if "master" in config:
                    master = config.get("master", "")
                    if not master.startswith("local"):
                        return True
                elif "host" in config or "cluster_id" in config:
                    # Databricks or other remote cluster
                    return True

        return False

    def get_recommendation_reason(
        self, node: ManifestNode, analysis_result: QueryAnalysisResult
    ) -> str:
        """
        Get human-readable explanation for engine selection.

        :param node: The node
        :param analysis_result: Query analysis result
        :returns: Explanation string
        """
        estimate = self._estimate_workload(node, analysis_result)
        engine = self._apply_selection_logic(estimate)

        reasons = []

        if estimate.estimated_data_mb > self.cluster_threshold_mb:
            reasons.append(
                f"Large dataset ({estimate.estimated_data_mb:.0f} MB / {estimate.estimated_data_mb / 1024:.1f} GB)"
            )
            if engine == "spark-local":
                reasons.append(
                    "No cluster configured (consider registering a Spark cluster)"
                )
        else:
            reasons.append(
                f"Small/medium workload ({estimate.estimated_data_mb:.0f} MB, {estimate.source_count} sources)"
            )

        if estimate.source_count > 5:
            reasons.append(f"Many sources ({estimate.source_count})")

        if estimate.complexity_score > 0.7:
            reasons.append(f"High complexity (score: {estimate.complexity_score:.2f})")

        reason_str = "; ".join(reasons)
        return f"Selected {engine}: {reason_str}"
