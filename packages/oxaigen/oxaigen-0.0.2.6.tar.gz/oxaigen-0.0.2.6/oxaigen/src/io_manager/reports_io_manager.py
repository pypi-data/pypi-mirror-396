# -*- coding: utf-8 -*-
import os
import io
import boto3
from typing import Any, Optional, cast
from dagster import IOManager, OutputContext, InputContext
from dagster_aws.s3 import S3Resource
from botocore.client import BaseClient  # type for any boto client


class S3ReportsIOManager(IOManager):
    """
    IO Manager for storing and retrieving notebook reports in S3.
    """

    def __init__(
            self,
            s3_resource: S3Resource,
            s3_bucket: str,
            s3_prefix: str = "reports",
    ):
        self.s3_resource = s3_resource
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self._s3_client: Optional[BaseClient] = None

    def _get_s3_client(self) -> BaseClient:
        """
        Get the boto3 S3 client, either by calling .get_client() on the resource
        or by treating the resource itself as the client.
        """
        if self._s3_client is None:
            # if this is a Dagster S3Resource, call get_client()
            if hasattr(self.s3_resource, "get_client"):
                client = self.s3_resource.get_client()  # type: ignore[attr-defined]
                # cast so MyPy knows it’s an S3 client
                self._s3_client = cast(BaseClient, client)
            else:
                # assume they passed in a raw boto3 client
                self._s3_client = cast(BaseClient, self.s3_resource)
        return self._s3_client

    def _get_s3_key(self, context) -> str:
        parts = [self.s3_prefix]  # Keep your top-level "reports" prefix
        if context.asset_key:
            parts.extend(context.asset_key.path[:-1])  # everything except final part (the filename)
        if getattr(context, "run_id", None):
            parts.append(context.run_id)
        parts.append(f"{context.asset_key.path[-1]}.ipynb")  # filename
        return "/".join(parts)

    def handle_output(self, context: OutputContext, obj: Any) -> None:
        s3_key = self._get_s3_key(context)
        client = self._get_s3_client()

        if isinstance(obj, bytes):
            client.put_object(Bucket=self.s3_bucket, Key=s3_key, Body=obj)
        else:
            buffer = io.BytesIO()
            buffer.write(obj)
            buffer.seek(0)
            client.upload_fileobj(buffer, self.s3_bucket, s3_key)

        context.add_output_metadata({
            "s3_path": f"s3://{self.s3_bucket}/{s3_key}",
        })

    def load_input(self, context: InputContext) -> Any:
        client = self._get_s3_client()

        upstream = context.upstream_output
        if upstream and "s3_path" in upstream.metadata:
            key = upstream.metadata["s3_path"].replace(f"s3://{self.s3_bucket}/", "")
            try:
                resp = client.get_object(Bucket=self.s3_bucket, Key=key)
                return resp["Body"].read()
            except Exception as e:
                raise RuntimeError(f"Failed to load {key} from S3: {e}")

        # fallback: list runs under prefix and pick the latest
        prefix = f"{self.s3_prefix}/{'/'.join(context.asset_key.path[:-1])}/"
        asset = context.asset_key.path[-1]

        try:
            runs = client.list_objects_v2(
                Bucket=self.s3_bucket, Prefix=prefix, Delimiter="/"
            ).get("CommonPrefixes", [])
            if not runs:
                raise RuntimeError(f"No runs found under {prefix}")
            latest_run = sorted(p["Prefix"] for p in runs)[-1]

            objs = client.list_objects_v2(
                Bucket=self.s3_bucket, Prefix=latest_run
            ).get("Contents", [])
            matches = [o for o in objs if o["Key"].endswith(f"{asset}.ipynb")]
            if not matches:
                raise RuntimeError(f"No notebook {asset}.ipynb in {latest_run}")
            latest_obj = sorted(matches, key=lambda o: o["LastModified"])[-1]

            resp = client.get_object(Bucket=self.s3_bucket, Key=latest_obj["Key"])
            return resp["Body"].read()

        except Exception as e:
            raise RuntimeError(f"Failed to load input for {asset}: {e}")
