# -*- coding: utf-8 -*-
import os
import json
import shutil
import tempfile
import psycopg2
from psycopg2 import sql
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from dagstermill.factory import execute_notebook
from typing import Callable, Iterable, Optional, Mapping, Union, Any, List, Set, Tuple
from dagster import define_asset_job, Shape, Field, AssetIn, Output, AssetKey, AssetsDefinition, JobDefinition

# Importing from private dagster classes (DagsterMill)
import dagster._check as check
from dagster._core.execution.context.compute import OpExecutionContext

from oxaigen.src.settings.settings import BaseSettingsInterface
from ..settings.settings import Settings
from ..notebook.notebook_pdf_generator import render_dagstermill_notebook_to_pdf
from ..notebook.s3_storage import S3ClientStorage
from .notebook_asset import define_notebook_as_asset

DEFAULT_REPORT_ASSET_PREFIX: List[str] = ["Oxaigen", "Reports"]
DEFAULT_REPORT_ASSET_GROUP_NAME = "Reports"
DEFAULT_REPORT_IO_MANAGER = "reports_io_manager"
DEFAULT_S3_STORAGE_PREFIX = "reports"
WORKSPACE_ID = "workspaceId"

FILES_DIR = "files"
CLEAN_FILES_DIR = "clean"


class S3StorageMetadata(BaseModel):
    """
    Pydantic model for S3 storage metadata.
    """
    PermanentNotebookLink: str
    PermanentPDFLink: str


def _execute_notebook_step(
        context: OpExecutionContext,
        name: str,
        notebook_path: str,
        save_notebook_on_failure: bool,
        settings: BaseSettingsInterface,
        config_schema: Optional[Union[Any, Mapping[str, Any]]] = None,
        **inputs
) -> tuple[str, str]:
    """
    Executes a Jupyter notebook as part of a Dagster step, saves both the executed
    and a cleaned version of the notebook to disk, and returns their file paths.

    The executed notebook is saved in the reports directory. A cleaned version is
    also created by removing the first and last cells, typically used to strip
    metadata or boilerplate from automated runs.

    Args:
        context (OpExecutionContext): The Dagster execution context for the current step.
        name (str): A name identifier for the notebook execution run.
        notebook_path (str): Path to the input notebook to be executed.
        save_notebook_on_failure (bool): Whether to save the notebook even if execution fails.
        settings (BaseSettingsInterface): Settings instance containing configuration
            such as the output directory path. Defaults to the global `settings` object.
        config_schema (Optional[Union[Any, Mapping[str, Any]]], optional): Optional config schema for
            validating run configuration. Not directly used in this function, but can be useful
            in surrounding pipeline definitions.
        **inputs: Arbitrary keyword arguments passed as parameters to the executed notebook.

    Returns:
        tuple[str, str]: A tuple containing:
            - The path to the executed notebook file.
            - The path to the cleaned notebook file (with first and last cells removed).
    """
    with tempfile.TemporaryDirectory() as output_notebook_dir:
        executed_notebook_path = execute_notebook(
            context.get_step_execution_context(),
            name=name,
            inputs=inputs,
            save_notebook_on_failure=save_notebook_on_failure,
            notebook_path=notebook_path,
            output_notebook_dir=output_notebook_dir,
        )

        # Paths
        reports_file_dir = os.path.join(settings.REPORTS_DIR, FILES_DIR)
        clean_subdir = os.path.join(reports_file_dir, CLEAN_FILES_DIR)

        os.makedirs(reports_file_dir, exist_ok=True)
        os.makedirs(clean_subdir, exist_ok=True)

        notebook_base_name = os.path.basename(executed_notebook_path)
        copied_notebook_path = os.path.join(reports_file_dir, notebook_base_name)
        cleaned_notebook_path = os.path.join(clean_subdir, notebook_base_name)

        # Copy the original executed notebook
        shutil.copy(executed_notebook_path, copied_notebook_path)

        # Create a cleaned version (remove first and last cell including output)
        with open(executed_notebook_path, "r", encoding="utf-8") as f:
            nb = json.load(f)

        if "cells" in nb and len(nb["cells"]) >= 3:
            nb["cells"] = nb["cells"][1:-1]

        with open(cleaned_notebook_path, "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=2)

        return copied_notebook_path, cleaned_notebook_path


def _generate_pdf_step(
        executed_notebook_path: str,
        settings: BaseSettingsInterface,
) -> str:
    """
    Converts an executed Jupyter notebook into a PDF report.

    This step cleans the notebook using a predefined cleaning function,
    then renders the cleaned version to PDF using a notebook-to-PDF renderer.
    The resulting PDF is saved to the reports directory.

    Args:
        executed_notebook_path (str): Path to the executed Jupyter notebook file.
        settings (BaseSettingsInterface): Settings instance containing configuration
            such as the reports directory path. Defaults to the global `settings` object.

    Returns:
        str: The file path to the generated PDF report.

    Raises:
        FileNotFoundError: If the notebook cleaning or PDF rendering fails at any step.
    """
    reports_dir = settings.REPORTS_DIR
    reports_file_dir = os.path.join(reports_dir, FILES_DIR)
    clean_reports_file_dir = os.path.join(reports_file_dir, CLEAN_FILES_DIR)

    notebook_base_name = os.path.basename(executed_notebook_path)

    pdf_generated: bool = render_dagstermill_notebook_to_pdf(
        working_directory=reports_dir,
        executed_notebook_file_name=notebook_base_name,
        file_directory=clean_reports_file_dir,
    )
    if pdf_generated is False:
        raise FileNotFoundError("Could not generate PDF from clean report notebook")

    output_pdf_path = os.path.join(clean_reports_file_dir, notebook_base_name.replace(".ipynb", ".pdf"))

    return output_pdf_path


def _store_files_to_s3_step(
        clean_notebook_path: str,
        output_pdf_path: str,
        run_id: str,
        name: str,
        settings: BaseSettingsInterface,
        asset_key_prefix: Optional[List[str]] = DEFAULT_REPORT_ASSET_PREFIX,
        s3_prefix: Optional[Union[str, List[str]]] = DEFAULT_S3_STORAGE_PREFIX
) -> S3StorageMetadata:
    """
    Uploads the cleaned notebook and corresponding PDF report to S3 and returns metadata.

    This step stores both the cleaned `.ipynb` file and the rendered `.pdf` file
    to structured paths in an S3 bucket, organized by `run_id` and `name`. The returned
    metadata includes permanent S3 links to both files.

    Args:
        clean_notebook_path (str): Local path to the cleaned Jupyter notebook file.
        output_pdf_path (str): Local path to the generated PDF report.
        run_id (str): Unique identifier for the notebook execution run.
        name (str): Name of the notebook, used in constructing the S3 filenames.
        settings (BaseSettingsInterface): Settings instance containing S3 configuration.
            Defaults to the global `settings` object.
        asset_key_prefix (List[str], Optional): the S3 Dagster Bucket directory path for the notebook asset
        s3_prefix (Union[str, List[str]]], Optional): the S3 Client Bucket directory path where the notebook and pdf will be stored.

    Returns:
        S3StorageMetadata: An object containing permanent S3 links for the uploaded notebook and PDF.
    """
    s3_storage = S3ClientStorage(settings=settings)

    # Normalize s3_prefix to a list
    if isinstance(s3_prefix, str):
        s3_prefix_parts = [s3_prefix]
    elif isinstance(s3_prefix, list):
        s3_prefix_parts = s3_prefix
    else:
        s3_prefix_parts = []

    # Construct full S3 path prefix
    s3_file_path = os.path.join(*(s3_prefix_parts + asset_key_prefix))
    notebook_s3_path = os.path.join(s3_file_path, run_id, f"{name}.ipynb")

    # Save the notebook
    s3_storage.save_file(file_path=clean_notebook_path, s3_path=notebook_s3_path)

    # Save the PDF
    pdf_s3_path = os.path.join(s3_file_path, run_id, f"{name}.pdf")
    s3_storage.save_file(file_path=output_pdf_path, s3_path=pdf_s3_path)

    return S3StorageMetadata(
        PermanentNotebookLink=f"S3://{settings.CLIENT_BUCKET}/{notebook_s3_path}",
        PermanentPDFLink=f"S3://{settings.CLIENT_BUCKET}/{pdf_s3_path}"
    )


def _insert_report_record(
        asset_key_prefix: List[str],
        name: str,
        notebook_link: str,
        pdf_link: str,
        run_id: str,
        config_dict: dict,
        settings: BaseSettingsInterface,
) -> int:
    """
    Inserts a new report entry into the reports database table and returns the generated record ID.

    The inserted record includes metadata such as the report name, S3 links to the notebook and PDF,
    run identifier, configuration schema, and a default status.

    Args:
        asset_key_prefix (List[str]): A list of string components representing the logical key prefix
            for the report (e.g. hierarchical folder-like structure).
        name (str): The name of the report or notebook.
        notebook_link (str): S3 URI pointing to the stored notebook file.
        pdf_link (str): S3 URI pointing to the stored PDF report.
        run_id (str): Unique identifier for the report execution run.
        config_dict (dict): Dictionary containing the serialized configuration schema used to
            generate the report.
        settings (BaseSettingsInterface): Settings instance providing access to the
            database connection URI. Defaults to the global `settings` object.

    Returns:
        int: The primary key (`itemId`) of the inserted report record.

    Raises:
        Exception: If any database error occurs during insertion, the error is printed and re-raised.
    """
    try:
        conn = psycopg2.connect(settings.PSYCOPG_CLIENT_DATABASE_URI)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        status: int = 1

        insert_query = sql.SQL("""
            INSERT INTO "reports"."Report" ("keyPrefix", "reportName", "notebookLink", "pdfLink", "runId", "configSchema", "status")
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING "itemId"
        """)
        cur.execute(insert_query,
                    (asset_key_prefix, name, notebook_link, pdf_link, run_id, json.dumps(config_dict), status))

        # Fetch the generated ID
        result = cur.fetchone()
        generated_id = result['itemId']

        conn.commit()
        cur.close()
        conn.close()

        return generated_id

    except Exception as e:
        print(f"Error inserting report record: {e}")
        if conn:  # noqa
            conn.rollback()  # noqa
        raise


def _make_oxaigen_report_asset_compute_function(
        asset_key_prefix: List[str],
        name: str,
        notebook_path: str,
        settings: BaseSettingsInterface,
        save_notebook_on_failure: Optional[bool] = False,
        s3_prefix: Optional[Union[str, List[str]]] = DEFAULT_S3_STORAGE_PREFIX,
        config_schema: Optional[Union[Any, Mapping[str, Any]]] = None,
        tags: Optional[Mapping[str, Any]] = None,
) -> Callable:
    """
    Creates a Dagster compute function that runs a notebook-based report pipeline.

    The returned function performs the following steps when executed within a Dagster
    pipeline:
        1. Executes a specified Jupyter notebook with given inputs.
        2. Generates a cleaned version of the notebook and converts it to a PDF.
        3. Uploads the notebook and PDF to S3, returning permanent links.
        4. Inserts a record into the reports database table with metadata.
        5. Yields the executed notebook as a Dagster output, including S3 metadata.
        6. Cleans up all temporary files created during execution.

    Args:
        asset_key_prefix (List[str]): Logical key prefix used for organizing report records and S3 paths.
        name (str): Unique name of the report, used for naming files and DB records.
        notebook_path (str): Path to the notebook to be executed.
        settings (BaseSettingsInterface): Settings object with config for S3, DB, and directories.
            Defaults to the global `settings` object.
        save_notebook_on_failure (bool, optional): If True, save the executed notebook even on failure, defaults to False
        s3_prefix (Union[str,List[str]], Optional): the S3 Client Bucket directory path where the notebook and pdf will
            be stored.
        config_schema (Optional[Union[Any, Mapping[str, Any]]], optional): Optional config schema for
            validating run configuration. Not directly used in this function, but can be useful
            in surrounding pipeline definitions.
        tags (Optional[Dict[str, Any]]): A dictionary of tags for the asset itself (not the op).
            These are visible in the Dagster UI. The tag `oxaigen_asset_type: report` will always
            be added and cannot be overridden.
    Returns:
        Callable: A Dagster compute function that can be used as an asset or op, yielding
            the notebook as a binary output with associated metadata.
    """

    def _t_fn(context: OpExecutionContext, **inputs) -> Iterable:
        check.param_invariant(
            isinstance(context.run_config, dict),
            "context",
            "StepExecutionContext must have valid run_config",
        )

        # Get execution context
        run_id = context.run_id
        config_dict = context.op_config

        # Track paths to delete at the end
        temp_paths = []

        try:
            # Step 1: Execute the notebook
            executed_notebook_path, cleaned_notebook_path = _execute_notebook_step(
                context=context,
                name=name,
                notebook_path=notebook_path,
                save_notebook_on_failure=save_notebook_on_failure,
                settings=settings,
                config_schema=config_schema,
                **inputs
            )
            temp_paths.extend([executed_notebook_path, cleaned_notebook_path])

            # Step 2: Generate the PDF
            output_pdf_path = _generate_pdf_step(
                executed_notebook_path=cleaned_notebook_path,
                settings=settings,
            )
            temp_paths.append(output_pdf_path)

            # Step 3: Store files to S3
            s3_storage_metadata: S3StorageMetadata = _store_files_to_s3_step(
                clean_notebook_path=cleaned_notebook_path,
                output_pdf_path=output_pdf_path,
                run_id=run_id,
                name=name,
                settings=settings,
                asset_key_prefix=asset_key_prefix,
                s3_prefix=s3_prefix
            )

            # Step 4: Insert a new record into the reports table
            _insert_report_record(
                asset_key_prefix=asset_key_prefix,
                name=name,
                settings=settings,
                notebook_link=s3_storage_metadata.PermanentNotebookLink,
                pdf_link=s3_storage_metadata.PermanentPDFLink,
                run_id=run_id,
                config_dict=config_dict
            )

            workspace_id = None
            try:
                workspace_id = context.op_config[WORKSPACE_ID]
            except KeyError:
                # workspaceId not provided by user (even though it's available in config_schema)
                # fallback to asset tag, which falls back to None...
                pass

            if workspace_id is None:
                if tags is not None:
                    if WORKSPACE_ID in tags.keys():
                        workspace_id = tags.get(WORKSPACE_ID, None)

            # Step 5: Yield notebook as Dagster output
            with open(executed_notebook_path, "rb") as fd:
                print(f"EXECUTED NOTEBOOK PATH: {executed_notebook_path}")
                yield Output(fd.read(), metadata={
                    "ReportUUID": run_id,
                    WORKSPACE_ID: workspace_id,
                    **s3_storage_metadata.dict(),
                })

        finally:
            # Step 6: Cleanup temporary files
            for path in temp_paths:
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"⚠️ Could not delete temp file: {path} — {e}")

    return _t_fn


def define_oxaigen_report_as_asset(
        name: str,
        file: str,
        description: str,
        settings: Optional[BaseSettingsInterface] = None,
        group: Optional[str] = DEFAULT_REPORT_ASSET_GROUP_NAME,
        asset_key_prefix: Optional[List[str]] = DEFAULT_REPORT_ASSET_PREFIX,
        s3_prefix: Optional[Union[str, List[str]]] = DEFAULT_S3_STORAGE_PREFIX,
        ins: Optional[Mapping[str, AssetIn]] = None,
        config_schema: Optional[Union[Any, Mapping[str, Any]]] = None,
        tags: Optional[Mapping[str, Any]] = None,
        required_resource_keys: Optional[Set[str]] = None,
        io_manager_key: Optional[str] = DEFAULT_REPORT_IO_MANAGER
) -> Tuple[AssetsDefinition, JobDefinition]:
    """
    Defines a Dagster asset for executing a Jupyter notebook report within the Oxaigen framework.

    This function wraps the report notebook execution pipeline into a reusable Dagster asset,
    which includes notebook execution, PDF generation, file storage on S3, and database
    record insertion. The returned asset integrates with Dagster’s IO manager and resource system.

    Args:
        name (str): Unique name for the report asset.
        file (str): Path to the Jupyter notebook file to execute.
        description (str): Description of the report asset for documentation purposes.
        settings (Optional[BaseSettingsInterface], optional): Configuration settings object.
            Defaults to the global `settings` instance.
        group (Optional[str], optional): Asset group name for organizing assets in Dagster.
            Defaults to `REPORT_ASSET_GROUP_NAME`.
        asset_key_prefix (Optional[List[str]], optional): Key prefix used to namespace the asset keys.
            Defaults to `REPORT_ASSET_PREFIX`.
        s3_prefix (Union[str,List[str]], Optional): the S3 Client Bucket directory path where the notebook and pdf will
            be stored.
        ins (Optional[Mapping[str, AssetIn]], optional): Input dependencies for the asset.
            Defaults to None.
        config_schema (Optional[Union[Any, Mapping[str, Any]]], optional): Configuration schema
            for validating run-time inputs. Defaults to None.
        tags (Optional[Dict[str, Any]]): A dictionary of tags for the asset itself (not the op).
            These are visible in the Dagster UI. The tag `oxaigen_asset_type: report` will always
            be added and cannot be overridden.
        required_resource_keys (Optional[Set[str]], optional): Set of resource keys required by the asset.
            Defaults to None.
        io_manager_key (Optional[str], optional): Key of the IO manager to use for this asset.
            Defaults to `DEFAULT_REPORT_IO_MANAGER`.

    Returns:
        Tuple[AssetDefinition, AssetJob]: A tuple containing:
            - The Dagster asset definition encapsulating the notebook report pipeline.
            - A Dagster job that runs the asset, named based on its full asset key joined by `__` and suffixed with `__job`.

    Example usage with `reports_io_manager`:

        ```python
        from dagster import Definitions
        from your_project.assets.report_assets import define_oxaigen_report_as_asset
        from oxaigen.src.io_manager.reports_io_manager import S3ReportsIOManager
        from dagster_aws.s3 import S3Resource

        s3_resource = S3Resource(...)
        reports_io_manager = S3ReportsIOManager(
            s3_resource=s3_resource,
            s3_bucket="your-s3-bucket-name",
            s3_prefix="reports",
            asset_key_prefix=["Oxaigen", "Reports"]
        )

        report_asset = define_oxaigen_report_as_asset(
            name="monthly_sales_report",
            file="reports/monthly_sales_report.ipynb",
            description="Generates monthly sales report notebook and PDF, uploads to S3 and logs metadata.",
            config_schema={"start_date": str, "end_date": str},
            io_manager_key="reports_io_manager"
        )

        defs = Definitions(
            assets=[report_asset],
            resources={
                "reports_io_manager": reports_io_manager,
                "s3_resource": s3_resource,
                # other resources as needed
            },
        )
        ```
    """
    if settings is None:
        settings = Settings()

    # Handle config_schema to ensure workspaceId field is present
    if config_schema is None:
        config_schema = Shape({
            WORKSPACE_ID: Field(int, is_required=False, description="The workspace UUID")
        })
    elif isinstance(config_schema, Shape) and WORKSPACE_ID not in config_schema.fields:
        # Create a new Shape with the existing fields plus the workspaceId field
        existing_fields = config_schema.fields.copy()
        existing_fields[WORKSPACE_ID] = Field(str, is_required=False, description="The workspace UUID")
        config_schema = Shape(existing_fields)
    elif not isinstance(config_schema, Shape):
        raise ValueError("Invalid config_schema, use Shape() from dagster")

    # Define report compute function (callable)
    oxaigen_report_asset_compute_function = _make_oxaigen_report_asset_compute_function(
        asset_key_prefix=asset_key_prefix,
        name=name,
        notebook_path=file,
        save_notebook_on_failure=True,
        s3_prefix=s3_prefix,
        settings=settings,
        config_schema=config_schema,
        tags=tags
    )

    # return dagster @asset wrapper asset variable
    notebook_asset = define_notebook_as_asset(
        asset_compute_function=oxaigen_report_asset_compute_function,
        key_prefix=asset_key_prefix,
        name=name,
        description=description,
        notebook_path=file,
        group_name=group,
        io_manager_key=io_manager_key,
        required_resource_keys=required_resource_keys,
        ins=ins,
        save_notebook_on_failure=True,
        config_schema=config_schema,
        tags=tags
    )

    # Construct asset key for job naming
    asset_key = AssetKey(path=(asset_key_prefix or []) + [name])
    notebook_asset_job_name = "__".join(asset_key.path) + "__job"

    # Create an asset job
    notebook_asset_job = define_asset_job(
        name=notebook_asset_job_name,
        selection=[notebook_asset.key]
    )

    return notebook_asset, notebook_asset_job
