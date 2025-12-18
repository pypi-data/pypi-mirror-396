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
from pathlib import Path
from typing import Any, Dict

import duckdb
from loguru import logger

from dcs_core.core.common.errors import DataChecksDataSourcesConnectionError
from dcs_core.core.common.models.data_source_resource import RawColumnInfo
from dcs_core.core.datasource.sql_datasource import SQLDataSource


class DuckDb(SQLDataSource):
    def __init__(self, data_source_name: str, data_connection: Dict):
        super().__init__(data_source_name, data_connection)
        self.connection = None
        self.use_sa_text_query = False
        self.regex_patterns = {
            "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
            "usa_phone": r"^(\+1[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}$",
            "email": r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            "usa_zip_code": r"^[0-9]{5}(?:-[0-9]{4})?$",
            "ssn": r"^[0-9]{3}-[0-9]{2}-[0-9]{4}$",
            "sedol": r"^[B-DF-HJ-NP-TV-XZ0-9]{6}[0-9]$",
            "lei": r"^[A-Z0-9]{18}[0-9]{2}$",
            "cusip": r"^[0-9A-Z]{9}$",
            "figi": r"^BBG[A-Z0-9]{9}$",
            "isin": r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$",
            "perm_id": r"^\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{3}$",
        }
        self.DEFAULT_NUMERIC_PRECISION = 16383

    def connect(self) -> Any:
        """
        Connect to the file data source
        """
        try:
            file_path = self.data_connection.get("file_path")
            self.connection = duckdb.connect(database=file_path)
            return self.connection
        except Exception as e:
            raise DataChecksDataSourcesConnectionError(f"Failed to connect to DuckDB: {e}")

    def is_connected(self) -> bool:
        """
        Check if the file data source is connected
        """
        return self.connection is not None

    def close(self):
        """
        Close the connection
        """
        logger.info("Closing DuckDB connection")
        if self.connection:
            self.connection.close()
        try:
            fp = self.data_connection.get("file_path")
            if fp and os.path.exists(fp):
                os.remove(fp)
        except Exception as e:
            logger.error(f"Failed to remove the file {self.data_connection.get('file_path')}: {e}")

    def qualified_table_name(self, table_name: str) -> str:
        """
        Get the qualified table name
        :param table_name: name of the table
        :return: qualified table name
        """
        return f'"{table_name}"'

    def quote_column(self, column: str) -> str:
        """
        Quote the column name
        :param column: name of the column
        :return: quoted column name
        """
        return f'"{column}"'

    def query_get_table_columns(
        self,
        table: str,
        schema: str | None = None,
    ) -> Dict[str, RawColumnInfo]:
        """
        Get the schema of a table.
        :param table: table name
        :return:  Dictionary with column names and their types
        """
        schema = schema or self.schema_name
        info_schema_path = ["information_schema", "columns"]
        if self.database:
            database = self.quote_database(self.database)
            info_schema_path.insert(0, database)

        query = f"""
            SELECT
                column_name,
                data_type,
                CASE WHEN data_type IN ('TIMESTAMP', 'TIME') THEN datetime_precision ELSE NULL END AS datetime_precision,
                CASE WHEN data_type = 'DECIMAL' THEN COALESCE(numeric_precision, 131072 + {self.DEFAULT_NUMERIC_PRECISION})
                     WHEN data_type IN ('DOUBLE', 'REAL', 'FLOAT') THEN numeric_precision
                     ELSE numeric_precision END AS numeric_precision,
                CASE WHEN data_type = 'DECIMAL' THEN COALESCE(numeric_scale, {self.DEFAULT_NUMERIC_PRECISION}) ELSE numeric_scale END AS numeric_scale,
                NULL AS collation_name,
                CASE WHEN data_type = 'VARCHAR' THEN character_maximum_length ELSE NULL END AS character_maximum_length
            FROM information_schema.columns
            WHERE table_name = '{table}'
            ORDER BY ordinal_position
        """

        rows = self.fetchall(query)
        if not rows:
            raise RuntimeError(f"{table}: Table, {schema}: Schema, does not exist, or has no columns")

        column_info = {
            r[0]: RawColumnInfo(
                column_name=self.safe_get(r, 0),
                data_type=self.safe_get(r, 1),
                datetime_precision=self.safe_get(r, 2),
                numeric_precision=self.safe_get(r, 3),
                numeric_scale=self.safe_get(r, 4),
                collation_name=self.safe_get(r, 5),
                character_maximum_length=self.safe_get(r, 6),
            )
            for r in rows
        }
        return column_info
