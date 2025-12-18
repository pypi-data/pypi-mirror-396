#  Copyright 2022-present, the Waterdip Labs Pvt. Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import duckdb
from azure.storage.blob import BlobServiceClient
from loguru import logger

from dcs_core.core.common.errors import (
    DatachecksColumnFetchError,
    DataChecksDataSourcesConnectionError,
    DatachecksTableFetchError,
)
from dcs_core.core.common.models.data_source_resource import RawColumnInfo
from dcs_core.core.datasource.file_datasource import FileDataSource


class AzureBlobDataSource(FileDataSource):
    def __init__(self, data_source_name: str, data_connection: Dict):
        super().__init__(data_source_name, data_connection)
        self.allowed_file_extensions = [".csv"]
        self.blob_service_client: Optional[BlobServiceClient] = None
        self.DEFAULT_NUMERIC_PRECISION = 16383
        self.connection = None

    def connect(self) -> Any:
        """
        Connect to the file data source
        """
        try:
            account_name = self.data_connection.get("account_name")
            container_name = self.data_connection.get("container_name")
            account_key = self.data_connection.get("account_key")
            endpoint_suffix = self.data_connection.get("endpoint_suffix", "core.windows.net")
            connection_str = f"https://{account_name}.blob.{endpoint_suffix}"
            blob_service_client = BlobServiceClient(account_url=connection_str, credential=account_key)
            self.blob_service_client = blob_service_client
            self.connection = blob_service_client.get_container_client(container=container_name)
            return self.connection
        except Exception as e:
            raise DataChecksDataSourcesConnectionError(f"Failed to connect to Azure Blob Storage: {e}")

    def is_connected(self) -> bool:
        """
        Check if the file data source is connected
        """
        return self.connection is not None

    def close(self):
        """
        Close the connection
        """
        self.connection.close()
        self.blob_service_client.close()
        self.connection = None
        self.blob_service_client = None

    def query_get_table_names(self) -> dict:
        """
        Query to get table names (blob names in this case)
        """
        if not self.is_connected():
            raise DataChecksDataSourcesConnectionError("Not connected to Azure Blob Storage")
        try:
            subfolder = self.data_connection.get("subfolder", "")
            blob_iterator = self.connection.list_blobs(name_starts_with=subfolder)
            blobs = [
                blob.name
                for blob in blob_iterator
                if len(blob.name.split("/")) == 1 and blob.name.endswith(tuple(self.allowed_file_extensions))
            ]
            return {"table": blobs}
        except Exception as e:
            raise DatachecksTableFetchError(f"Failed to list blobs: {e}")

    def safe_get(self, lst, idx, default=None):
        return lst[idx] if 0 <= idx < len(lst) else default

    def query_get_database_version(self) -> str:
        """
        Get the database version
        :return: version string
        """
        api_version = self.blob_service_client.api_version
        return api_version

    def _download_to_path(self, table_name: str, path: str):
        """Download blob to path"""
        blob_client = self.connection.get_blob_client(blob=table_name)
        logger.info(f"Downloading {table_name} to {path}")
        try:
            with open(path, "wb") as f:
                stream = blob_client.download_blob()
                for chunk in stream.chunks():
                    f.write(chunk)
        except Exception as e:
            raise DataChecksDataSourcesConnectionError(f"Failed to download blob '{table_name}': {e}")
