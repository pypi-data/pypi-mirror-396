"""
Feature API v2 - Declarative Feature Definitions.

This module provides the Feature API v2, which offers both a fluent builder pattern
for defining features and backward compatibility with the legacy API. It consolidates
all feature definition functionality into a single cohesive module.

Public API:
    - FeatureBuilder: The builder class for declarative feature definitions
    - Feature(): Factory function for legacy API compatibility
    - AggregateFunction: Enum of aggregation functions (re-exported from enums)

Supporting Classes:
    - SelectConfig: Configuration for column selection
    - AggregateConfig: Configuration for aggregations
    - BackfillConfig: Configuration for stream backfill
    - WindowedFeatureRef: Reference to a specific time window
    - FeatureSourceType: Enum for batch vs stream sources

Example Usage:
    ```python
    import featureform as ff
    from datetime import timedelta

    @ff.entity
    class User:
        # Builder Pattern - validated automatically during registration
        transaction_count = (
            ff.Feature()
            .from_dataset(batch_features)
            .select(entity="CustomerID", value="Amount", timestamp="Timestamp")
            .aggregate(
                function=ff.AggregateFunction.COUNT,
                windows=[timedelta(days=7)]
            )
        )

        # Legacy API (still supported)
        legacy_feature = ff.Feature(
            transformation[["CustomerID", "Amount", "Timestamp"]],
            type=ff.Float32,
            variant="v1",
        )
    ```
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from ..enums import AggregateFunction, ResourceType, ScalarType
from ..resources import (
    AggregateFeature,
    AttributeFeature,
    FeatureVariant,
    ResourceColumnMapping,
)

__all__ = [
    # Main API
    "Feature",
    "FeatureBuilder",
    # Re-exported enum
    "AggregateFunction",
    # Supporting classes and enums
    "FeatureSourceType",
    "FeatureType",
    "SelectConfig",
    "AggregateConfig",
    "BackfillConfig",
    "BuiltFeatures",
    "AggregateBuiltFeatures",
    "AttributeBuiltFeature",
    # Utility functions
    "format_window_suffix",
]


# =============================================================================
# Supporting Classes
# =============================================================================


class FeatureSourceType(str, Enum):
    """Type of source for a feature."""

    BATCH = "batch"
    STREAM = "stream"


class FeatureType(str, Enum):
    """Type of feature.

    This enum distinguishes between different kinds of features,
    which determines how they can be accessed and used.
    """

    AGGREGATE = (
        "aggregate"  # Time-windowed aggregate features (e.g., COUNT over 7 days)
    )
    ATTRIBUTE = "attribute"  # Simple point-in-time attribute features


def format_window_suffix(window: timedelta) -> str:
    """Format a timedelta as a string suffix (e.g., '7d', '1h')."""
    total_seconds = int(window.total_seconds())
    if total_seconds >= 86400 and total_seconds % 86400 == 0:
        return f"{total_seconds // 86400}d"
    elif total_seconds >= 3600 and total_seconds % 3600 == 0:
        return f"{total_seconds // 3600}h"
    elif total_seconds >= 60 and total_seconds % 60 == 0:
        return f"{total_seconds // 60}m"
    else:
        return f"{total_seconds}s"


@dataclass
class SelectConfig:
    """Configuration for selected columns in a feature definition."""

    entity: str
    value: str
    timestamp: str = ""


@dataclass
class AggregateConfig:
    """Configuration for feature aggregation."""

    function: AggregateFunction
    windows: List[timedelta]


@dataclass
class BackfillConfig:
    """Configuration for backfilling stream features from batch data."""

    source: Any
    entity: str
    value: str
    timestamp: str


class BuiltFeatures(ABC):
    """
    Abstract base class for built features.

    This is the result of building a FeatureBuilder. Concrete implementations are:
    - AggregateBuiltFeatures: For features with time windows (e.g., COUNT over 7 days)
    - AttributeBuiltFeature: For simple attribute features without time windows

    Each FeatureVariant has its own variant field that can be updated during
    equivalence resolution.

    This wrapper is set as the entity attribute (e.g., User.transaction_count)
    and provides access to individual features.

    Example:
        # Aggregate features - use bracket indexing
        User.transaction_count[timedelta(days=7)]

        # Attribute features - use name_variant()
        User.account_age.name_variant()

        # Both types - get all features
        User.transaction_count.get_all_features()
    """

    def __init__(self, base_name: str, base_variant: str):
        self._base_name = base_name
        self._base_variant = base_variant

    @property
    @abstractmethod
    def feature_type(self) -> FeatureType:
        """Return the type of this built feature."""
        ...

    @abstractmethod
    def get_all_features(self) -> List[FeatureVariant]:
        """Return all FeatureVariant objects."""
        ...

    @abstractmethod
    def name_variant(self) -> Tuple[str, str]:
        """Return the (name, variant) tuple.

        For aggregate features, raises an error directing users to use bracket indexing.
        For attribute features, returns the feature's name and variant.
        """
        ...

    @abstractmethod
    def __getitem__(self, window: timedelta) -> FeatureVariant:
        """Get the FeatureVariant for a specific time window.

        For aggregate features, returns the FeatureVariant for the specified window.
        For attribute features, raises TypeError.
        """
        ...

    def get_resource_type(self) -> ResourceType:
        return ResourceType.FEATURE_VARIANT

    @abstractmethod
    def __repr__(self) -> str: ...


class AggregateBuiltFeatures(BuiltFeatures):
    """
    Built features for aggregate features with time windows.

    Contains multiple FeatureVariant objects, one per time window (e.g., 1d, 7d, 30d).
    Access specific windows using bracket notation: `feature[timedelta(days=7)]`

    Example:
        @ff.entity
        class User:
            transaction_count = (
                ff.Feature()
                .from_dataset(transactions)
                .select(entity="user_id", value="amount", timestamp="ts")
                .aggregate(
                    function=ff.AggregateFunction.COUNT,
                    windows=[timedelta(days=1), timedelta(days=7)]
                )
            )

        # Access specific window
        User.transaction_count[timedelta(days=7)]

        # Get all windows
        User.transaction_count.get_all_features()
    """

    def __init__(
        self,
        features: Dict[timedelta, FeatureVariant],
        base_name: str,
        base_variant: str,
    ):
        super().__init__(base_name, base_variant)
        self._features = features

    @property
    def feature_type(self) -> FeatureType:
        return FeatureType.AGGREGATE

    def __getitem__(self, window: timedelta) -> FeatureVariant:
        """Get the FeatureVariant for a specific time window.

        Args:
            window: The time window duration (e.g., timedelta(days=7))

        Returns:
            FeatureVariant for the specified window

        Raises:
            KeyError: If the specified window doesn't exist
        """
        if window not in self._features:
            available = [format_window_suffix(w) for w in self._features.keys()]
            raise KeyError(
                f"Window {format_window_suffix(window)} not found. "
                f"Available windows: {available}"
            )
        return self._features[window]

    def name_variant(self) -> Tuple[str, str]:
        """Raises ValueError - use bracket indexing for aggregate features."""
        raise ValueError(
            "Use bracket indexing (e.g., feature[timedelta(days=7)]) to access "
            "specific windows for aggregate features."
        )

    def get_all_features(self) -> List[FeatureVariant]:
        """Return all FeatureVariant objects for all time windows."""
        return list(self._features.values())

    def __repr__(self) -> str:
        windows = [format_window_suffix(w) for w in self._features.keys()]
        return f"AggregateBuiltFeatures({self._base_name}, windows={windows})"


class AttributeBuiltFeature(BuiltFeatures):
    """
    Built feature for an attribute feature without time windows.

    Contains a single FeatureVariant representing a simple point-in-time attribute.

    Example:
        @ff.entity
        class User:
            account_age = (
                ff.Feature()
                .from_dataset(user_profiles)
                .select(entity="user_id", value="age_days", timestamp="updated_at")
            )

        # Get name and variant
        User.account_age.name_variant()

        # Get the feature
        User.account_age.get_all_features()
    """

    def __init__(
        self,
        feature: FeatureVariant,
        base_name: str,
        base_variant: str,
    ):
        super().__init__(base_name, base_variant)
        self._feature = feature

    @property
    def feature_type(self) -> FeatureType:
        return FeatureType.ATTRIBUTE

    def __getitem__(self, window: timedelta) -> FeatureVariant:
        """Raises TypeError - attribute features cannot be indexed."""
        raise TypeError(
            f"'{self._base_name}' is not an aggregate feature and cannot be indexed. "
            f"Use name_variant() or get_all_features() instead."
        )

    def name_variant(self) -> Tuple[str, str]:
        """Return the (name, variant) tuple for this attribute feature."""
        return self._feature.name_variant()

    def get_all_features(self) -> List[FeatureVariant]:
        """Return the single FeatureVariant as a list."""
        return [self._feature]

    def __repr__(self) -> str:
        return f"AttributeBuiltFeature({self._base_name}, variant={self._base_variant})"


# =============================================================================
# FeatureBuilder Class
# =============================================================================


class FeatureBuilder:
    """
    Builder class for declaratively defining features using a fluent API.

    This class provides a builder pattern for defining features with method chaining.
    Features are automatically validated and registered when used with the @ff.entity
    decorator.

    Example:
        ```python
        @ff.entity
        class User:
            # Simple feature
            account_balance = (
                ff.Feature()
                .from_dataset(batch_features)
                .select(entity="CustomerID", value="Balance", timestamp="Timestamp")
            )

            # Aggregated feature with multiple time windows
            transaction_count = (
                ff.Feature()
                .from_dataset(batch_features)
                .select(entity="CustomerID", value="Amount", timestamp="Timestamp")
                .aggregate(
                    function=ff.AggregateFunction.COUNT,
                    windows=[timedelta(days=1), timedelta(days=7)]
                )
            )
        ```
    """

    def __init__(self):
        """Initialize an empty FeatureBuilder for the builder pattern."""
        # Feature identification
        # base_name: The base feature name (e.g., "transaction_count")
        #   For aggregate features, window suffixes are appended (e.g., "transaction_count_7d")
        self.base_name: Optional[str] = None

        # initial_variant: The user's proposed variant for all generated features.
        #
        # This field is named "initial" because the value represents a proposed variant
        # that may be changed during the registration flow. When `create_all()` is called,
        # the server's equivalence resolution checks if an existing feature with matching
        # semantics already exists. If an equivalent is found, the actual
        # `FeatureVariant.variant` will be updated to match the existing equivalent variant,
        # overriding the value specified here.
        #
        # Flow:
        #   1. User sets initial_variant via variant() builder method
        #   2. FeatureVariant objects are created with variant=initial_variant
        #   3. During create_all(), _get_and_set_equivalent_variant() queries the server
        #   4. If equivalent found: FeatureVariant.variant is updated to the existing variant
        #   5. If no equivalent: FeatureVariant.variant remains as initial_variant
        self.initial_variant: Optional[str] = None
        self.entity: Optional[Any] = None

        # Feature metadata
        self.owner: str = ""
        self.description: str = ""
        self.tags: List[str] = []
        self.properties: Dict[str, str] = {}
        self.value_type: Optional[Union[ScalarType, str]] = None

        # Source configuration
        self.source: Optional[Any] = None
        self.source_type: Optional[FeatureSourceType] = None

        # Column selection
        self.select_config: Optional[SelectConfig] = None

        # Aggregation configuration
        self.aggregate_config: Optional[AggregateConfig] = None

        # Backfill configuration (for stream features)
        self.backfill_config: Optional[BackfillConfig] = None

        # Built features (set after build() is called)
        self._built_features: Optional[BuiltFeatures] = None

    # =========================================================================
    # Builder Pattern Methods
    # =========================================================================

    def from_dataset(self, source: Any) -> "FeatureBuilder":
        """
        Set the batch dataset source for this feature.

        Args:
            source: A registered source (transformation result or table source)

        Returns:
            self: For method chaining

        Raises:
            ValueError: If a source has already been set
        """
        if self.source is not None:
            raise ValueError(
                "Source already set. from_dataset() or from_stream() can only be called once."
            )
        self.source = source
        self.source_type = FeatureSourceType.BATCH
        return self

    def from_stream(self, source: Any) -> "FeatureBuilder":
        """
        Set the streaming source for this feature.

        Args:
            source: A registered streaming source

        Returns:
            self: For method chaining

        Raises:
            ValueError: If a source has already been set
        """
        if self.source is not None:
            raise ValueError(
                "Source already set. from_dataset() or from_stream() can only be called once."
            )
        self.source = source
        self.source_type = FeatureSourceType.STREAM
        return self

    def select(
        self,
        entity: str,
        value: str,
        timestamp: str = "",
    ) -> "FeatureBuilder":
        """
        Select the columns to use for this feature.

        Args:
            entity: Column name containing the entity identifier
            value: Column name containing the feature value
            timestamp: Column name containing the timestamp (optional)

        Returns:
            self: For method chaining

        Raises:
            ValueError: If select() has already been called
        """
        if self.select_config is not None:
            raise ValueError("select() can only be called once per FeatureBuilder.")
        self.select_config = SelectConfig(
            entity=entity,
            value=value,
            timestamp=timestamp,
        )
        return self

    def aggregate(
        self,
        function: AggregateFunction,
        windows: List[timedelta],
    ) -> "FeatureBuilder":
        """
        Configure time-windowed aggregation for this feature.

        This method must be called after select() to specify aggregation
        over the selected columns.

        Args:
            function: The aggregation function (COUNT, MEAN, SUM, MIN, MAX, etc.)
            windows: List of time windows to aggregate over

        Returns:
            self: For method chaining

        Raises:
            ValueError: If select() has not been called first, if aggregate() has
                       already been called, or if no windows specified
        """
        if self.select_config is None:
            raise ValueError(
                "select() must be called before aggregate(). "
                "Use .select(entity=..., value=..., timestamp=...).aggregate(...)"
            )
        if self.aggregate_config is not None:
            raise ValueError("aggregate() can only be called once per FeatureBuilder.")
        if not windows:
            raise ValueError("At least one window must be specified")
        self.aggregate_config = AggregateConfig(
            function=function,
            windows=windows,
        )
        return self

    def backfill_from(
        self,
        source: Any,
        entity: str,
        value: str,
        timestamp: str,
    ) -> "FeatureBuilder":
        """
        Configure backfill from a batch source (for stream features).

        This is used to populate historical data for stream features
        from an existing batch dataset with potentially different column names.

        Args:
            source: The batch source to backfill from
            entity: Entity column name in the backfill source
            value: Value column name in the backfill source
            timestamp: Timestamp column name in the backfill source

        Returns:
            self: For method chaining

        Raises:
            ValueError: If not a stream feature, or if backfill already configured
        """
        if self.source_type != FeatureSourceType.STREAM:
            raise ValueError("backfill_from() can only be used with stream features")
        if self.backfill_config is not None:
            raise ValueError(
                "backfill_from() can only be called once per FeatureBuilder."
            )
        self.backfill_config = BackfillConfig(
            source=source,
            entity=entity,
            value=value,
            timestamp=timestamp,
        )
        return self

    def name(self, name: str) -> "FeatureBuilder":
        """
        Set the base name for this feature.

        This method allows manually specifying the feature name instead of
        deriving it from the entity attribute name.

        Args:
            name: The base name for the feature

        Returns:
            self: For method chaining

        Example:
            ```python
            feature = (
                ff.Feature()
                .name("custom_feature_name")
                .variant("v1")
                .from_dataset(source)
                .select(entity="user_id", value="amount", timestamp="ts")
            )
            ```
        """
        self.base_name = name
        return self

    def variant(self, variant: str) -> "FeatureBuilder":
        """
        Set the initial/proposed variant for this feature.

        This method allows manually specifying the feature variant instead of
        using an auto-generated or default variant. The value provided here is
        considered "initial" or "proposed" because it may be changed during the
        registration process.

        **Equivalence Resolution Behavior:**

        During `client.apply()` (which calls `create_all()`), the server performs
        equivalence resolution to detect if an existing feature with matching
        semantics already exists. This affects the final variant used:

        - **If an equivalent feature is found:** The `FeatureVariant.variant` will
          be updated to match the existing equivalent variant, overriding the value
          specified here. This ensures semantic deduplication across the system.

        - **If no equivalent is found:** The variant specified here will be used
          as-is when creating the new feature.

        This means that calling `.variant("my_v1")` does not guarantee the final
        feature will have variant `"my_v1"` - it sets the proposed variant that
        will be used if no equivalent exists.

        Args:
            variant: The proposed variant string for the feature

        Returns:
            self: For method chaining

        Example:
            ```python
            feature = (
                ff.Feature()
                .name("transaction_count")
                .variant("production_v2")  # Proposed variant; may change if equivalent exists
                .from_dataset(source)
                .select(entity="user_id", value="amount", timestamp="ts")
            )
            ```
        """
        self.initial_variant = variant
        return self

    # =========================================================================
    # Resource Interface Methods
    # =========================================================================

    def name_variant(self) -> Tuple[str, str]:
        """Return the (name, variant) tuple for this feature."""
        if self.base_name is None:
            raise ValueError("Feature base_name not set")
        if self.initial_variant is None:
            raise ValueError("Feature initial_variant not set")
        return (self.base_name, self.initial_variant)

    def get_resource_type(self) -> ResourceType:
        """Return the resource type for this feature."""
        return ResourceType.FEATURE_VARIANT

    def to_key(self) -> Tuple[ResourceType, str, str]:
        """Return the unique key for this resource."""
        if self.base_name is None:
            raise ValueError("Feature base_name not set")
        if self.initial_variant is None:
            raise ValueError("Feature initial_variant not set")
        return self.get_resource_type(), self.base_name, self.initial_variant

    def _has_aggregation(self) -> bool:
        """Check if this builder has aggregation configured."""
        return self.aggregate_config is not None

    def _is_stream(self) -> bool:
        """Check if this is a stream feature."""
        return self.source_type == FeatureSourceType.STREAM

    def get_windows(self) -> List[timedelta]:
        """Get the list of configured windows, or an empty list if not aggregated."""
        if self.aggregate_config is None:
            return []
        return self.aggregate_config.windows

    # =========================================================================
    # Build Method
    # =========================================================================

    def build(self) -> BuiltFeatures:
        """
        Build and return BuiltFeatures containing FeatureVariant(s).

        This method validates the configuration and creates the appropriate
        FeatureVariant resources. For aggregated features with multiple windows,
        one FeatureVariant is created per window.

        Each FeatureVariant has its own variant field that can be updated
        during equivalence resolution.

        Note: Before calling build(), the following fields should be normalized:
        - entity: Should be a string (entity name), not an EntityRegistrar
        - owner: Should have a default value if not set
        - value_type: Should be a ScalarType, not None or string

        Returns:
            BuiltFeatures: Wrapper containing FeatureVariant(s)

        Raises:
            ValueError: If required configuration is missing
        """
        # Validate required fields
        if self.source is None:
            raise ValueError(
                "Feature source not set. Use from_dataset() or from_stream()"
            )
        if self.select_config is None:
            raise ValueError("Feature columns not selected. Use select()")
        if self.base_name is None:
            raise ValueError("Feature base_name not set")

        # Use pre-normalized values from builder
        source_name_variant = self._get_source_name_variant()

        # Get column configuration
        entity_column = self.select_config.entity
        value_column = self.select_config.value
        timestamp_column = self.select_config.timestamp

        has_aggregation = self._has_aggregation()

        if has_aggregation:
            # Create one FeatureVariant per window
            features: Dict[timedelta, FeatureVariant] = {}
            for window in self.aggregate_config.windows:
                window_suffix = format_window_suffix(window)
                feature_name = f"{self.base_name}_{window_suffix}"

                aggregate_def = AggregateFeature(
                    name=feature_name,
                    input_column=value_column,
                    input_type=self.value_type,
                    function=self.aggregate_config.function,
                    time_window=window,
                )

                feature_variant = FeatureVariant(
                    created=None,
                    name=feature_name,
                    variant=self.initial_variant,
                    source=source_name_variant,
                    value_type=self.value_type,
                    entity=self.entity,
                    owner=self.owner,
                    provider="",
                    description=self.description,
                    schedule="",
                    location=ResourceColumnMapping(
                        entity=entity_column,
                        value=value_column,
                        timestamp=timestamp_column,
                    ),
                    tags=self.tags,
                    properties=self.properties,
                    feature_definition=aggregate_def,
                )
                features[window] = feature_variant

            built_features: BuiltFeatures = AggregateBuiltFeatures(
                features=features,
                base_name=self.base_name,
                base_variant=self.initial_variant,
            )
        else:
            # Create a single attribute feature
            attribute_def = AttributeFeature(
                name=self.base_name,
                input_column=value_column,
                input_type=self.value_type,
            )

            feature_variant = FeatureVariant(
                created=None,
                name=self.base_name,
                variant=self.initial_variant,
                source=source_name_variant,
                value_type=self.value_type,
                entity=self.entity,
                owner=self.owner,
                provider="",
                description=self.description,
                schedule="",
                location=ResourceColumnMapping(
                    entity=entity_column,
                    value=value_column,
                    timestamp=timestamp_column,
                ),
                tags=self.tags,
                properties=self.properties,
                feature_definition=attribute_def,
            )

            built_features = AttributeBuiltFeature(
                feature=feature_variant,
                base_name=self.base_name,
                base_variant=self.initial_variant,
            )

        # Store reference for bracket indexing access
        self._built_features = built_features

        return built_features

    # =========================================================================
    # Registration Methods
    # =========================================================================

    def register(self) -> None:
        """
        Register this feature with the global registrar.

        This method is called by the @ff.entity decorator to register
        the feature with the Featureform backend.
        """
        from . import global_registrar

        global_registrar.register_feature_builder(self)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _get_source_name_variant(self) -> Tuple[str, str]:
        """Get the (name, variant) tuple from the source."""
        if hasattr(self.source, "name_variant"):
            return self.source.name_variant()
        elif isinstance(self.source, tuple) and len(self.source) == 2:
            return self.source
        else:
            raise ValueError(
                f"Source must have a 'name_variant()' method or be a (name, variant) tuple. "
                f"Got: {type(self.source).__name__}"
            )


# =============================================================================
# Feature Factory Function
# =============================================================================


def Feature(*args, **kwargs):
    """
    Create a Feature definition.

    This is the main entry point for defining features. It supports both
    the legacy API and the new builder pattern.

    **Legacy API** (pass transformation_args as first positional argument):
        ```python
        @ff.entity
        class User:
            avg_transactions = ff.Feature(
                transformation[["CustomerID", "Amount", "Timestamp"]],
                type=ff.Float32,
                variant="quickstart",
            )
        ```

    **Builder Pattern** (no arguments, use method chaining):
        ```python
        @ff.entity
        class User:
            account_balance = (
                ff.Feature()
                .from_dataset(batch_features)
                .select(
                    entity="CustomerID",
                    value="Balance",
                    timestamp="Timestamp"
                )
            )

            transaction_count = (
                ff.Feature()
                .from_dataset(batch_features)
                .select(
                    entity="CustomerID",
                    value="Amount",
                    timestamp="Timestamp"
                )
                .aggregate(
                    function=ff.AggregateFunction.COUNT,
                    windows=[timedelta(days=1), timedelta(days=7)]
                )
            )
        ```

    Both patterns can be used together in the same entity class, allowing
    for seamless migration from the legacy API to the builder pattern.

    Returns:
        FeatureBuilder (no args) or FeatureColumnResource (with args)
    """
    if args or kwargs:
        # Legacy API - delegate to FeatureColumnResource
        from .column_resources import FeatureColumnResource

        return FeatureColumnResource(*args, **kwargs)
    else:
        # Builder Pattern - return new FeatureBuilder
        return FeatureBuilder()
