# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Entity decorator for Featureform.

This module contains the @entity decorator for registering entities and their
associated features and labels.
"""

from .column_resources import (
    EmbeddingColumnResource,
    FeatureColumnResource,
    LabelColumnResource,
    MultiFeatureColumnResource,
)
from .feature_api import FeatureBuilder
from .variants import Variants

__all__ = ["entity"]


# Import register_entity from the module that will contain Registrar
def register_entity(name: str):
    """Register an entity. This will be replaced with actual implementation."""
    from . import global_registrar

    return global_registrar.register_entity(name)


def entity(cls):
    """
    Class decorator for registering entities and their associated features and labels.

    **Examples**
    ```python
    @ff.entity
    class User:
        avg_transactions = ff.Feature()
        fraudulent = ff.Label()

        # Using the new builder pattern
        account_balance = (
            ff.Feature()
            .from_dataset(batch_features)
            .select(entity="CustomerID", value="Balance", timestamp="Timestamp")
        )
    ```

    Returns:
        entity (EntityRegistrar): Decorated entity registrar with features/labels as attributes
    """
    from . import global_registrar

    # 1. Use the lowercase name of the class as the entity name
    entity_obj = register_entity(cls.__name__.lower())
    # 2. Given the Feature/Label/Variant class constructors are evaluated
    #    before the entity decorator, apply the entity name to their
    #    respective name dictionaries prior to registration
    for attr_name in cls.__dict__:
        attr_value = cls.__dict__[attr_name]

        if isinstance(
            attr_value,
            (FeatureColumnResource, LabelColumnResource, EmbeddingColumnResource),
        ):
            resource = attr_value
            resource.name = attr_name if resource.name == "" else resource.name
            resource.entity = entity_obj
            resource.register()
            # Set the resource as an attribute on the entity object
            setattr(entity_obj, attr_name, resource)

        elif isinstance(attr_value, FeatureBuilder):
            # Handle the new builder pattern
            builder = attr_value
            # Set base_name from attribute name if not explicitly set
            if builder.base_name is None:
                builder.base_name = attr_name
            # Set initial_variant from global run if not set
            if builder.initial_variant is None:
                builder.initial_variant = global_registrar.get_run()
            # Normalize values before build() so build() is a pure function
            builder.entity = global_registrar._normalize_entity_reference(entity_obj)
            builder.owner = (
                builder.owner
                if builder.owner
                else global_registrar.must_get_default_owner()
            )
            builder.value_type = global_registrar._normalize_value_type(
                builder.value_type
            )
            # register_feature_builder returns BuiltFeatures containing FeatureVariants
            built_features = global_registrar.register_feature_builder(builder)
            # Set the BuiltFeatures as an attribute on the entity object
            # This allows User.feature_name to return the BuiltFeatures wrapper
            setattr(entity_obj, attr_name, built_features)

        elif isinstance(attr_value, Variants):
            variants = attr_value
            for variant_key, resource in variants.resources.items():
                resource.name = attr_name if resource.name == "" else resource.name
                resource.entity = entity_obj
                resource.register()
            # Set the variants object as an attribute on the entity object
            setattr(entity_obj, attr_name, variants)

        elif isinstance(attr_value, MultiFeatureColumnResource):
            multi_feature = attr_value
            multi_feature_resources = multi_feature.features
            for resource in multi_feature_resources:
                setattr(entity_obj, resource.name, resource)
                resource.entity = entity_obj
                resource.register()
            # Set the MultiFeature object itself as an attribute on the entity object
            setattr(entity_obj, attr_name, multi_feature)

    # Return the entity object so it can be used in the code
    return entity_obj
