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
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator

import duckdb
from loguru import logger

from dcs_core.core.common.models.data_source_resource import RawColumnInfo
from dcs_core.core.datasource.base import DataSource
from dcs_core.integrations.databases.duck_db import DuckDb


class FileDataSource(DataSource, ABC):
    """
    Abstract class for File data sources
    """

    def __init__(self, data_source_name: str, data_connection: Dict):
        super().__init__(data_source_name, data_connection)
        self.temp_dir_name = "tmp"

    @contextmanager
    def as_duckdb(self, table_name: str) -> Iterator["DuckDb"]:
        """Returns a DuckDB instance for the given table name"""
        duckdb_path = self.load_file_to_duckdb(table_name)
        duck_db_ds = DuckDb(data_source_name=self.data_source_name, data_connection={"file_path": duckdb_path})
        try:
            duck_db_ds.connect()
            yield duck_db_ds
        finally:
            duck_db_ds.close()

    @abstractmethod
    def query_get_table_names(self) -> dict:
        """
        Query to get table names
        """
        pass

    @abstractmethod
    def query_get_database_version(self) -> str:
        """
        Get the database version
        :return: version string
        """
        pass

    @abstractmethod
    def _download_to_path(self, table_name: str, path: str) -> None:
        """Vendor-specific download"""
        pass

    def load_file_to_duckdb(self, table_name: str) -> str:
        """Template method"""
        os.makedirs(self.temp_dir_name, exist_ok=True)

        ext = Path(table_name).suffix
        if not ext:
            raise ValueError(f"Invalid file name {table_name}")

        temp_path = f"{self.temp_dir_name}/{uuid.uuid4()}{ext}"

        try:
            self._download_to_path(table_name, temp_path)
            return self._load_path_to_duckdb(temp_path, table_name)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"Cleaned up temp file {temp_path}")

    def _load_path_to_duckdb(self, path: str, table_name: str) -> str:
        """Shared DuckDB loading logic"""
        tmp_dir = self.temp_dir_name
        duckdb_path = f"{tmp_dir}/{uuid.uuid4()}.duckdb"
        table_stem = Path(table_name).stem

        logger.info(f"Loading {path} into DuckDB")

        conn = None
        try:
            conn = duckdb.connect(database=duckdb_path, read_only=False)
            conn.execute(
                f'CREATE TABLE "{table_stem}" AS SELECT * FROM read_csv_auto(?)',
                [path],
            )
            logger.info(f"Successfully loaded data into {duckdb_path}")
            return duckdb_path
        except Exception as e:
            logger.warning(f"read_csv_auto failed: {e}. Trying with ALL_VARCHAR=TRUE")
            try:
                if conn:
                    conn.close()
                conn = duckdb.connect(database=duckdb_path, read_only=False)
                conn.execute(
                    f'CREATE TABLE "{table_stem}" AS ' f"SELECT * FROM read_csv(?, ALL_VARCHAR=TRUE, SAMPLE_SIZE=-1)",
                    [path],
                )
                logger.info(f"Successfully loaded data with ALL_VARCHAR into {duckdb_path}")
                return duckdb_path
            except Exception as fallback_error:
                logger.error(f"Failed to load CSV into DuckDB: {fallback_error}")
                if os.path.exists(duckdb_path):
                    os.remove(duckdb_path)
                raise
        finally:
            if conn:
                conn.close()
