"""
    Helper function to create, rename, delete custom tables and columns in the model
"""

import copy
import re
import logging
from typing import Dict, List, Optional
from .internals.cosmicfrog_api import CosmicFrogAPI
from .internals.decorators import requires_parameter


class CustomTablesAndColumns:
    """
    Helper class to create, rename, delete custom tables and columns in the model
    """

    def __init__(self, model_name: str, app_key: str, log: logging.Logger):

        assert log, "Helper class requires a Logger"
        self.log: logging.Logger = log

        if not model_name:
            self.__handle_error__("", "Model name is required.")

        if not app_key:
            self.__handle_error__("", "App key is required.")

        self.model_name = model_name
        self._app_key = app_key

        self.api = CosmicFrogAPI(app_key=self._app_key)

    def __validate_identifier__(self, name: str, id_type: str) -> bool:
        """
        Validate an identifier (table or column name).
        Raises ValueError if invalid.
        """
        regex = r"^[a-zA-Z][a-zA-Z0-9_]*$"

        if not name:
            self.__handle_error__("", f"{id_type.capitalize()} name is required.")
        if not re.match(regex, name):
            self.__handle_error__(
                "",
                f"{id_type.capitalize()} name '{name}' must start with a letter and contain only letters, numbers, and underscores.",
            )
        if len(name) > 63:
            self.__handle_error__(
                "",
                f"{id_type.capitalize()} name '{name}' must be less than 63 characters.",
            )

        return True

    def __handle_error__(self, correlation_id: str, message: str) -> None:
        """
        Log an error and return a response
        """
        self.log.error("%s %s", correlation_id, message)
        raise ValueError(message)

    @requires_parameter("table_name")
    def create_table(self, table_name: str) -> Dict[str, str]:
        """
        Create a custom table in the model

        Args:
            table_name: str -- Name of the table to create

        Returns:
            dict: A dictionary containing 'status' and 'message'.
        """
        self.log.info(f"Creating custom table: {table_name}")

        self.__validate_identifier__(table_name, "table")

        res = self.api.create_table(self.model_name, table_name)
        self.log.info(f"Create table response: {res}")

        return {
            "status": res.get("result", "error"),
            "message": f"Table '{table_name}' created successfully",
        }

    @requires_parameter("table_name")
    @requires_parameter("new_table_name")
    def rename_table(self, table_name: str, new_table_name: str) -> Dict[str, str]:
        """
        Rename a custom table in the model

        Args:
            table_name: str -- Name of the table to rename
            new_table_name: str -- New name for the table

        Returns:
            dict: A dictionary containing 'status' and 'message'.
        """
        self.log.info(f"Renaming custom table: {table_name} to {new_table_name}")

        self.__validate_identifier__(new_table_name, "table")

        res = self.api.rename_table(self.model_name, table_name, new_table_name)
        self.log.info(f"Rename table response: {res}")

        return {
            "status": res.get("result", "error"),
            "message": f"Table '{table_name}' renamed to '{new_table_name}'",
        }

    @requires_parameter("table_name")
    def delete_table(self, table_name: str) -> Dict[str, str]:
        """
        Delete a custom table in the model

        Args:
            table_name: str -- Name of the table to delete

        Returns:
            dict: A dictionary containing 'status' and 'message'.
        """
        self.log.info(f"Deleting custom table: {table_name}")

        if not table_name:
            self.__handle_error__("", "Table name is required")

        res = self.api.delete_table(self.model_name, table_name)
        self.log.info(f"Delete table response: {res}")

        return {
            "status": res.get("result", "error"),
            "message": res.get("message", ""),
        }

    @requires_parameter("table_name")
    def get_pk_custom_columns(self, table_name: str) -> List[str]:
        """
        Get primary key custom columns for a certain table

        Args:
            table_name: str -- Name of the table to get primary key columns for

        Returns:
            list: A list of primary key column names.
        """
        self.log.info(f"Getting primary key custom columns for table: {table_name}")
        response_data = self.api.get_pk_custom_columns(self.model_name, table_name)
        if response_data.get("result") == "success":
            return [
                column["columnName"]
                for column in response_data.get("customColumns", [])
                if column.get("isTableKeyColumn", True)
            ]

        self.log.error(f"Error: {response_data.get('message')}")
        return []

    def get_custom_tables(self) -> List[str]:
        """
        Get all custom tables in the model

        Returns:
            list: A list of custom table names.
        """

        response_data = self.api.get_custom_tables(self.model_name)
        if response_data.get("result") == "success":
            return response_data.get("customTables", [])

        self.log.error(f"Error: {response_data.get('message')}")
        return []

    @requires_parameter("table_name")
    def get_all_custom_columns(self, table_name) -> Dict[str, str]:
        """
        Get all custom columns for a certain table

        Args:
            table_name: str -- Name of the table to get custom columns for

        Returns:
            dict: A dictionary containing 'status' and 'message'.
        """

        self.log.info(f"Getting all custom columns for table: {table_name}")
        res = self.api.get_all_custom_columns(self.model_name, table_name)
        self.log.info(f"Get all custom columns response: {res}")

        return {
            "status": res.get("result", "error"),
            "message": res.get("customColumns", ""),
        }

    @requires_parameter("table_name")
    @requires_parameter("column_name")
    def create_custom_column(
        self,
        table_name: str,
        column_name: str,
        data_type: str = "text",
        key_column: bool = False,
        pseudo: bool = True,
    ) -> Dict[str, str]:
        """
        Create a custom column in a custom table

        Args:
            table_name: str -- Name of the table to create the column in
            column_name: str -- Name of the column to create
            data_type: str -- Data type of the column. Valid types: text, integer, date, timestamp, bool, numeric
            key_column: bool -- Will be included as part of the unique record identification when importing (updating, inserting) data to the table
            pseudo: bool -- Data of any type can be freely imported and will behave as the defined data type in UI (Grids, Maps, Dashboards)

        Returns:
            dict: A dictionary containing 'status' and 'message'.
        """
        VALID_DATA_TYPES = ["text", "integer", "date", "timestamp", "bool", "numeric"]
        self.log.info(f"Creating custom column: {column_name} in table: {table_name}")
        if not table_name:
            self.__handle_error__("", "Table name is required")

        if not column_name:
            self.__handle_error__("", "Column name is required")

        self.__validate_identifier__(column_name, "column")

        if not data_type:
            self.__handle_error__("", "Data type is required")

        if data_type not in VALID_DATA_TYPES:
            self.__handle_error__(
                "",
                f"Invalid data type: '{data_type}'. Valid types are: {', '.join(VALID_DATA_TYPES)}",
            )
        if pseudo:
            true_data_type = "text"
        else:
            true_data_type = data_type

        res = self.api.create_custom_column(
            self.model_name,
            table_name=table_name,
            column_name=column_name,
            data_type=data_type,
            is_table_key_column=key_column,
            true_data_type=true_data_type,
        )
        self.log.info(f"Create custom column response: {res}")

        return {
            "status": res.get("result", "error"),
            "message": res.get("message", ""),
        }

    @requires_parameter("columns")
    def bulk_create_custom_columns(
        self, columns: List[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Bulk create custom columns.

        Each column should be a dictionary with the following keys:
            - table_name: str
            - column_name: str
            - data_type: str (Optional) - Default is 'text'
            - key_column: bool (Optional) - Default is False
            - pseudo: bool (Optional) - Default is False

        Example Args:
            columns = [
                {
                    "table_name": "Facilities",
                    "column_name": "Custom1",
                    "data_type": "integer",
                },
                {
                    "table_name": "Facilities",
                    "column_name": "Custom2"
                },
                {
                    "table_name": "Customers",
                    "column_name": "Custom3",
                }
            ]

        Args:
            columns: list -- List of columns to create

        Returns:
            dict: A dictionary containing 'status', 'message', 'added', 'skipped', and 'errors'.
        """
        self.log.info(f"Bulk creating custom columns: {columns}")

        local_columns = copy.deepcopy(columns)

        for column in local_columns:
            if not column.get("table_name"):
                self.__handle_error__(
                    "", f"Table name is required. Error found in column: {column}"
                )

            if not column.get("column_name"):
                self.__handle_error__(
                    "", f"Column name is required, Error found in column: {column}"
                )

            self.__validate_identifier__(column.get("column_name"), "column")

            if not column.get("data_type"):
                column["dataType"] = "text"
            else:
                column["dataType"] = column.get("data_type")
                column.pop("data_type", None)

            column["tableName"] = column.get("table_name").lower()
            column.pop("table_name", None)

            column["columnName"] = column.get("column_name").lower()
            column.pop("column_name", None)

            if column.get("pseudo"):
                column["trueDataType"] = "text"
                column.pop("pseudo", None)
            else:
                column["trueDataType"] = column["dataType"]
                column.pop("pseudo", None)

            if column.get("key_column"):
                column["isTableKeyColumn"] = column.get("key_column")
                column.pop("key_column", None)

        res = self.api.bulk_create_custom_columns(self.model_name, local_columns)
        self.log.info(f"Bulk create custom columns response: {res}")

        return {
            "status": res.get("result", "error"),
            "message": res.get("message", ""),
            "added": res.get("added", []),
            "skipped": res.get("skipped", []),
            "errors": res.get("errors", []),
        }

    @requires_parameter("table_name")
    @requires_parameter("column_name")
    def delete_custom_column(self, table_name: str, column_name: str) -> Dict[str, str]:
        """
        Delete a custom column in a custom table

        Args:
            table_name: str -- Name of the table to delete the column from
            column_name: str -- Name of the column to delete

        Returns:
            dict: A dictionary containing 'status' and 'message'.
        """
        self.log.info(f"Deleting custom column: {column_name} from table: {table_name}")
        if not table_name:
            self.__handle_error__("", "Table name is required")

        if not column_name:
            self.__handle_error__("", "Column name is required")

        res = self.api.delete_custom_column(self.model_name, table_name, column_name)
        self.log.info(f"Delete custom column response: {res}")

        return {
            "status": res.get("result", "error"),
            "message": res.get("message", ""),
        }

    @requires_parameter("table_name")
    @requires_parameter("column_name")
    def edit_custom_column(
        self,
        table_name: str,
        column_name: str,
        new_column_name: Optional[str] = None,
        data_type: Optional[str] = None,
        key_column: Optional[bool] = None,
    ) -> Dict[str, str]:
        """
        Edit a custom column in a custom table

        Args:
            table_name: str -- Name of the table to edit the column in
            column_name: str -- Name of the column to edit
            new_column_name: str -- New name of the column
            data_type: str -- New data type of the column (e.g. text, integer, float, date, boolean)
            key_column: bool -- Will be included as part of the unique record identification when importing (updating, inserting) data to the table
            pseudo: bool -- Data of any type can be freely imported and will behave as the defined data type in UI (Grids, Maps, Dashboards)

        Returns:
            dict: A dictionary containing 'status' and 'message'.
        """
        self.log.info(f"Editing custom column: {column_name} in table: {table_name}")
        if not table_name:
            self.__handle_error__("", "Table name is required")

        if not column_name:
            self.__handle_error__("", "Column name is required")

        if new_column_name:
            self.__validate_identifier__(new_column_name, "new_column_name")

        res = self.api.edit_custom_column(
            self.model_name,
            table_name=table_name,
            column_name=column_name,
            new_column_name=new_column_name,
            data_type=data_type,
            is_table_key_column=key_column,
        )
        self.log.info(f"Edit custom column response: {res}")

        return {
            "status": res.get("result", "error"),
            "message": res.get("message", ""),
        }
