# -*- coding: utf-8 -*-
import json
import logging
from typing import Any, Dict, List, Optional, Hashable

import sqlalchemy
import numpy as np
import pandas as pd
from dagster import ConfigurableIOManager, InputContext, OutputContext


class OxaigenDbIOManager(ConfigurableIOManager):
    """Oxaigen IOManager to handle loading the contents of tables as pandas DataFrames.

    Does not handle cases where data is written to different schemas for different outputs, and
    uses the name of the asset key as the table name.
    """

    con_string: str

    def handle_output(self, context: Optional[OutputContext], obj: Any) -> None:
        if isinstance(obj, pd.DataFrame):
            asset_key: Optional[str] = None
            schema_name: str = "public"
            if context is not None:
                try:
                    asset_key = context.asset_key.path[-1]
                    schema_name = context.asset_key.path[-2].lower()
                except Exception as e:
                    print("AssetKey is not defined, cannot upload asset to database")
                    logging.error(e)

            if asset_key:
                # Generic pass: Replace string representations of null values with None
                obj = obj.applymap(
                    lambda v: None if isinstance(v, str) and v in {"NaN", "null", "[]"} else v
                )

                # For each column, if any value is a dict or list, convert those values to JSON strings
                for col in obj.columns:
                    if obj[col].apply(lambda x: isinstance(x, (dict, list))).any():
                        obj[col] = obj[col].apply(
                            lambda v: json.dumps(v) if isinstance(v, (dict, list)) and v is not None else v
                        )

                # Convert numeric types correctly
                for col in obj.select_dtypes(include=[np.number]).columns:
                    obj[col] = obj[col].map(
                        lambda x: int(x) if isinstance(x, np.integer) else float(x) if isinstance(x, np.floating) else x
                    )

                # Dynamically detect columns that now contain JSON strings for proper type mapping
                json_cols: List[str] = []
                for col in obj.columns:
                    # if any cell is a string that looks like JSON (starts with '{' or '['), mark as JSON column
                    if obj[col].apply(lambda x: isinstance(x, str) and (
                            x.startswith("{") or x.startswith("[")) and x != "null").any():
                        json_cols.append(col)

                # Use the exact type expected by pandas to_sql
                dtype_mapping: Dict[Hashable, Any] = {col: sqlalchemy.types.JSON() for col in json_cols}

                # CREATE SCHEMA IF NOT EXISTS
                engine = sqlalchemy.create_engine(self.con_string)
                try:
                    with engine.begin() as conn:
                        conn.execute(sqlalchemy.text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
                except sqlalchemy.exc.IntegrityError:
                    # Schema already exists, continue
                    pass

                obj.to_sql(
                    name=asset_key,
                    schema=schema_name,
                    con=self.con_string,
                    index=False,
                    if_exists="replace",
                    dtype=dtype_mapping,
                )
            else:
                raise KeyError("AssetKey is not defined, cannot save output to database")

    def load_input(self, context: InputContext) -> pd.DataFrame:
        """Load the contents of a table as a pandas DataFrame.

        Uses the "public" schema as default if asset key doesn't contain a schema name.
        """
        try:
            model_name = context.asset_key.path[-1]

            # Default to "public" schema if asset key doesn't have at least 2 path components
            schema_name = "public"
            if len(context.asset_key.path) >= 2:
                schema_name = context.asset_key.path[-2].lower()

            return pd.read_sql(f"""SELECT * FROM "{schema_name}"."{model_name}";""", con=self.con_string)
        except Exception as error:
            try:
                model_name = context.asset_key.path[-1]
            except:
                model_name = "unknown, assetKey is not defined"
            print(f"Cannot load database table input for asset {str(model_name)}, error: {error}")
            logging.error(f"Cannot load database table input for asset {str(model_name)}, error: {error}")
            raise