# -*- coding: utf-8 -*-
import logging
from typing import Any, Mapping, Optional
from dagster_dbt import DagsterDbtTranslator
from dagster import AssetKey

DEFAULT_GROUP_NAME = "DataWarehouse"


class _TemplateDagsterDbtTranslator(DagsterDbtTranslator):
    """
    THIS CLASS MUST NEVER BE USED DIRECTLY!

    use create_custom_dbt_translator_class() instead as it also
    inserts the required get_asset_key() class method.
    """
    oxaigen_group_name = DEFAULT_GROUP_NAME

    @classmethod
    def get_group_name(cls, dbt_resource_props: Mapping[str, Any]) -> Optional[str]:
        return cls.oxaigen_group_name

    @classmethod
    def get_metadata(cls, dbt_resource_props: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Custom function to set EXTRA metadata key-value pairs for a DBT asset
        """
        return {"Oxaigen": "DBT resource"}

    @classmethod
    def get_description(cls, dbt_resource_props: Mapping[str, Any]) -> str:
        """
        Custom function to set the description of the DBT asset which by default includes the raw SQL code.
        This behaviour can be adapted below
        """
        try:
            raw_code = dbt_resource_props["raw_code"]
        except Exception:
            logging.error(f"Could not fetch DBT MODEL RAW CODE, please verify all DBT models are correctly configured.")
            logging.debug(f"DEBUG: Please verify the following DBT MODEL: {str(dbt_resource_props)}")
            raw_code = ''

        custom_description = dbt_resource_props["name"] + "\n" + raw_code
        return custom_description


def create_oxaigen_dbt_translator_class(
        custom_prefix: str,
        source_tags_as_asset_prefix: bool = True,
        group_prefix: Optional[str] = None,
        source_group_prefix: Optional[str] = None,
        group_name: Optional[str] = DEFAULT_GROUP_NAME
):
    class OxaigenDagsterDbtTranslator(_TemplateDagsterDbtTranslator):
        oxaigen_group_name = group_name  # Set class attribute directly

        def get_asset_key(self, dbt_resource_props: Mapping[str, Any]) -> AssetKey:
            # Start with the default key
            original_key = super().get_asset_key(dbt_resource_props)
            path = list(original_key.path)

            if dbt_resource_props["resource_type"] == "source":
                # Apply source tags or group prefixes as before
                if source_tags_as_asset_prefix:
                    for tag in dbt_resource_props.get("tags", []):
                        path.insert(0, tag)
                if source_group_prefix:
                    path.insert(0, source_group_prefix)
            else:
                # Non-source models get the custom prefix
                if group_prefix:
                    path.insert(0, group_prefix)

                # Rename the final component according to alias or derive a title-cased name
                if dbt_resource_props.get("alias"):
                    path[-1] = dbt_resource_props["alias"]
                else:
                    last = path[-1]
                    if last.startswith("prod_"):
                        last = last.replace("prod_", "", 1)
                    # Title-case and remove underscores
                    new_name = last.replace("_", " ").title().replace(" ", "")
                    path[-1] = new_name
                    # Also title-case the schema part
                    if len(path) >= 2:
                        path[-2] = new_name.title()

                # Finally, add the custom_prefix
                path.insert(0, custom_prefix)

            # Return a new AssetKey built from the modified path
            return AssetKey(path)

    return OxaigenDagsterDbtTranslator()
