# -*- coding: utf-8 -*-
from typing import Any, Callable, Iterable, Mapping, Optional, Set, Union, cast
from dagstermill.factory import _clean_path_for_windows
from dagster import (
    AssetIn,
    AssetKey,
    AssetsDefinition,
    PartitionsDefinition,
    ResourceDefinition,
    RetryPolicy,
    SourceAsset,
    asset,
)

# Importing from private dagster classes (DagsterMill)
import dagster._check as check
from dagster._config.pythonic_config import Config, infer_schema_from_config_class
from dagster._config.pythonic_config.type_check_utils import safe_is_subclass
from dagster._core.definitions.events import CoercibleToAssetKey, CoercibleToAssetKeyPrefix
from dagster._core.execution.context.compute import OpExecutionContext
from dagster._core.storage.tags import COMPUTE_KIND_TAG
from dagster._utils.tags import normalize_tags


def define_notebook_as_asset(
        asset_compute_function: Callable,
        name: str,
        notebook_path: str,
        key_prefix: Optional[CoercibleToAssetKeyPrefix] = None,
        ins: Optional[Mapping[str, AssetIn]] = None,
        deps: Optional[Iterable[Union[CoercibleToAssetKey, AssetsDefinition, SourceAsset]]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        config_schema: Optional[Union[Any, Mapping[str, Any]]] = None,
        required_resource_keys: Optional[Set[str]] = None,
        resource_defs: Optional[Mapping[str, ResourceDefinition]] = None,
        description: Optional[str] = None,
        partitions_def: Optional[PartitionsDefinition] = None,
        op_tags: Optional[Mapping[str, Any]] = None,
        tags: Optional[Mapping[str, Any]] = None,
        group_name: Optional[str] = None,
        io_manager_key: Optional[str] = None,
        retry_policy: Optional[RetryPolicy] = None,
        save_notebook_on_failure: bool = False,
        non_argument_deps: Optional[Union[Set[AssetKey], Set[str]]] = None,
) -> AssetsDefinition:
    """Creates a Dagster asset for a Jupyter notebook.

    Arguments:
        name (str): The name for the asset
        notebook_path (str): Path to the backing notebook
        key_prefix (Optional[Union[str, Sequence[str]]]): If provided, the asset's key is the
            concatenation of the key_prefix and the asset's name, which defaults to the name of
            the decorated function. Each item in key_prefix must be a valid name in dagster (ie only
            contains letters, numbers, and _) and may not contain python reserved keywords.
        ins (Optional[Mapping[str, AssetIn]]): A dictionary that maps input names to information
            about the input.
        deps (Optional[Sequence[Union[AssetsDefinition, SourceAsset, AssetKey, str]]]): The assets
            that are upstream dependencies, but do not pass an input value to the notebook.
        config_schema (Optional[ConfigSchema): The configuration schema for the asset's underlying
            op. If set, Dagster will check that config provided for the op matches this schema and fail
            if it does not. If not set, Dagster will accept any config provided for the op.
        metadata (Optional[Dict[str, Any]]): A dict of metadata entries for the asset.
        required_resource_keys (Optional[Set[str]]): Set of resource handles required by the notebook.
        description (Optional[str]): Description of the asset to display in the Dagster UI.
        partitions_def (Optional[PartitionsDefinition]): Defines the set of partition keys that
            compose the asset.
        op_tags (Optional[Dict[str, Any]]): A dictionary of tags for the op that computes the asset.
            Frameworks may expect and require certain metadata to be attached to an op. Values that
            are not strings will be json encoded and must meet the criteria that
            `json.loads(json.dumps(value)) == value`.
        tags (Optional[Dict[str, Any]]): A dictionary of tags for the asset itself (not the op).
            These are visible in the Dagster UI. The tag `oxaigen_asset_type: report` will always
            be added and cannot be overridden.
        group_name (Optional[str]): A string name used to organize multiple assets into groups. If not provided,
            the name "default" is used.
        resource_defs (Optional[Mapping[str, ResourceDefinition]]):
            (Experimental) A mapping of resource keys to resource definitions. These resources
            will be initialized during execution, and can be accessed from the
            context within the notebook.
        io_manager_key (Optional[str]): A string key for the IO manager used to store the output notebook.
            If not provided, the default key output_notebook_io_manager will be used.
        retry_policy (Optional[RetryPolicy]): The retry policy for the op that computes the asset.
        save_notebook_on_failure (bool): If True and the notebook fails during execution, the failed notebook will be
            written to the Dagster storage directory. The location of the file will be printed in the Dagster logs.
            Defaults to False.
        non_argument_deps (Optional[Union[Set[AssetKey], Set[str]]]): Deprecated, use deps instead. Set of asset keys that are
            upstream dependencies, but do not pass an input to the asset.

    Examples:
        .. code-block:: python

            from dagstermill import define_dagstermill_asset
            from dagster import asset, AssetIn, AssetKey
            from sklearn import datasets
            import pandas as pd
            import numpy as np

            @asset
            def iris_dataset():
                sk_iris = datasets.load_iris()
                return pd.DataFrame(
                    data=np.c_[sk_iris["data"], sk_iris["target"]],
                    columns=sk_iris["feature_names"] + ["target"],
                )

            iris_kmeans_notebook = define_notebook_as_asset(
                name="iris_kmeans_notebook",
                notebook_path="/path/to/iris_kmeans.ipynb",
                ins={
                    "iris": AssetIn(key=AssetKey("iris_dataset"))
                }
            )
    """
    check.str_param(name, "name")
    check.str_param(notebook_path, "notebook_path")
    check.bool_param(save_notebook_on_failure, "save_notebook_on_failure")

    required_resource_keys = set(
        check.opt_set_param(required_resource_keys, "required_resource_keys", of_type=str)
    )
    ins = check.opt_mapping_param(ins, "ins", key_type=str, value_type=AssetIn)

    if isinstance(key_prefix, str):
        key_prefix = [key_prefix]

    key_prefix = check.opt_list_param(key_prefix, "key_prefix", of_type=str)

    default_description = f"This asset is backed by the notebook at {notebook_path}"
    description = check.opt_str_param(description, "description", default=default_description)

    io_mgr_key = check.opt_str_param(
        io_manager_key, "io_manager_key", default="output_notebook_io_manager"
    )

    user_tags = normalize_tags(op_tags)
    if op_tags is not None:
        check.invariant(
            "notebook_path" not in op_tags,
            "user-defined op tags contains the `notebook_path` key, but the `notebook_path` key"
            " is reserved for use by Dagster",
        )
        check.invariant(
            COMPUTE_KIND_TAG not in op_tags,
            f"user-defined op tags contains the `{COMPUTE_KIND_TAG}` key, but the `{COMPUTE_KIND_TAG}` key is reserved for"
            " use by Dagster",
        )

    default_op_tags = {
        "notebook_path": _clean_path_for_windows(notebook_path),
        COMPUTE_KIND_TAG: "ipynb",
    }

    # Validate and merge tags
    if tags is not None:
        if not isinstance(tags, dict):
            raise TypeError("tags must be a dictionary")

    asset_tags = {
        **tags,
        "oxaigen_asset_type": "report",
    }

    if safe_is_subclass(config_schema, Config):
        config_schema = infer_schema_from_config_class(cast("type[Config]", config_schema))

    @asset(
        name=name,
        key_prefix=key_prefix,
        ins=ins,
        deps=deps,
        metadata=metadata,
        description=description,
        config_schema=config_schema,
        required_resource_keys=required_resource_keys,
        resource_defs=resource_defs,
        partitions_def=partitions_def,
        op_tags={**user_tags, **default_op_tags},
        tags=asset_tags,
        group_name=group_name,
        output_required=False,
        io_manager_key=io_mgr_key,
        retry_policy=retry_policy,
        non_argument_deps=non_argument_deps
    )
    def asset_fn(context: OpExecutionContext, **inputs):
        return asset_compute_function(context, **inputs)

    return asset_fn
