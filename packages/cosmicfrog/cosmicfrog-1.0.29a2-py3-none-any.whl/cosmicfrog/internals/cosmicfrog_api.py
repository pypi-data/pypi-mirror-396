"""
Low-level HTTP client for CosmicFrog storage/custom tables APIs.

This mirrors the request pattern of datastar_api.DatastarAPI so that
the dependency on the `requests` library is confined to this file.

Intended to be used internally by higher-level helpers (e.g.,
CustomTablesAndColumns) and to enable future refactors without changing
external call sites.
"""

from __future__ import annotations

import os
import sys
import traceback
from typing import Any, Dict, List, Optional

import requests
from requests import Response, request


# Base URL can be overridden via environment variable. Normalize to have no trailing slash.
_DEFAULT_BASE = "https://api.optilogic.app/v0"
API_BASE: str = os.getenv("ATLAS_API_BASE_URL", _DEFAULT_BASE).strip("/")


class ApiError(Exception):
    """Exception class to contain dependency on requests module to this file."""

    def __init__(
        self, message: str, original_exception: Optional[BaseException] = None
    ):
        super().__init__(message)
        self.original_exception: Optional[BaseException] = original_exception
        self.trace: str = traceback.format_exc()


class CosmicFrogAPI:
    """
    Base client for CosmicFrog storage APIs dealing with custom tables/columns.

    Authentication uses an app key. If not supplied to the constructor, it is
    read from the environment variable OPTILOGIC_JOB_APPKEY or from an app.key
    file next to the executing script (first line), consistent with DatastarAPI.
    """

    app_key: Optional[str] = None
    DEFAULT_TIMEOUT: int = 60

    def __init__(self, *, app_key: Optional[str] = None):
        if app_key:
            CosmicFrogAPI.app_key = app_key

        if CosmicFrogAPI.app_key is None:
            env_key = os.getenv("OPTILOGIC_JOB_APPKEY")
            if env_key:
                CosmicFrogAPI.app_key = env_key

        if CosmicFrogAPI.app_key is None:
            script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
            key_path = os.path.join(script_dir, "app.key")
            if os.path.exists(key_path):
                with open(key_path, "r", encoding="utf-8") as f:
                    CosmicFrogAPI.app_key = f.readline().strip()

        if not CosmicFrogAPI.app_key:
            raise ValueError(
                "App key not found. Place an app.key file next to your script or set OPTILOGIC_JOB_APPKEY. "
                "Manage keys at: https://optilogic.app/#/user-account?tab=appkey"
            )

        if len(CosmicFrogAPI.app_key) != 51 or not CosmicFrogAPI.app_key.startswith(
            "op_"
        ):
            raise ValueError(
                "Valid appkey is required (format: op_..., 51 characters). "
                "Get your key at: https://optilogic.app/#/user-account?tab=appkey"
            )

        # Request headers (match casing from Datastar; header names are case-insensitive)
        self.auth_req_header = {
            "x-app-key": CosmicFrogAPI.app_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API, returning a parsed JSON object
        or a minimal success wrapper with raw text if the response is not JSON.
        """

        url = f"{API_BASE}/{endpoint.lstrip('/')}"
        _timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT

        try:
            response: Response = request(
                method=method,
                url=url,
                headers=self.auth_req_header,
                json=data,
                params=params,
                timeout=_timeout,
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            raise ApiError(f"HTTP request failed: {e}", e) from e

    # ==================== Custom Tables ====================

    def create_table(self, model_name: str, table_name: str) -> Dict[str, Any]:
        payload = {"tableName": table_name.lower()}
        return self._request("POST", f"storage/{model_name}/custom-table", data=payload)

    def rename_table(
        self, model_name: str, table_name: str, new_table_name: str
    ) -> Dict[str, Any]:
        payload = {
            "tableName": table_name.lower(),
            "newTableName": new_table_name.lower(),
        }
        return self._request("PUT", f"storage/{model_name}/custom-table", data=payload)

    def delete_table(self, model_name: str, table_name: str) -> Dict[str, Any]:
        payload = {"tableName": table_name}
        return self._request(
            "DELETE", f"storage/{model_name}/custom-table", data=payload
        )

    def get_custom_tables(self, model_name: str) -> Dict[str, Any]:
        return self._request("GET", f"storage/{model_name}/custom-tables")

    # ==================== Custom Columns ====================

    def get_all_custom_columns(
        self, model_name: str, table_name: str
    ) -> Dict[str, Any]:
        # The existing implementation sends a body with GET; we mirror the shape but pass via body for parity.
        payload = {"tableName": table_name}
        return self._request(
            "GET", f"storage/{model_name}/custom-columns", data=payload
        )

    def get_pk_custom_columns(self, model_name: str, table_name: str) -> Dict[str, Any]:
        params = {"tableName": table_name}
        return self._request(
            "GET", f"storage/{model_name}/custom-columns", params=params
        )

    def create_custom_column(
        self,
        model_name: str,
        *,
        table_name: str,
        column_name: str,
        data_type: str,
        is_table_key_column: bool,
        true_data_type: str,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "tableName": table_name.lower(),
            "columnName": column_name.lower(),
            "dataType": data_type,
            "isTableKeyColumn": is_table_key_column,
            "trueDataType": true_data_type,
        }
        return self._request(
            "POST", f"storage/{model_name}/custom-column", data=payload
        )

    def bulk_create_custom_columns(
        self, model_name: str, columns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        payload = {"columns": columns}
        return self._request(
            "POST", f"storage/{model_name}/custom-columns", data=payload
        )

    def delete_custom_column(
        self, model_name: str, table_name: str, column_name: str
    ) -> Dict[str, Any]:
        payload = {"tableName": table_name, "columnName": column_name}
        return self._request(
            "DELETE", f"storage/{model_name}/custom-column", data=payload
        )

    def edit_custom_column(
        self,
        model_name: str,
        *,
        table_name: str,
        column_name: str,
        new_column_name: Optional[str] = None,
        data_type: Optional[str] = None,
        is_table_key_column: Optional[bool] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "tableName": table_name.lower(),
            "columnName": column_name,
        }
        if new_column_name:
            payload["newColumnName"] = new_column_name.lower()
        if data_type:
            payload["dataType"] = data_type
            payload["trueDataType"] = data_type
        if is_table_key_column is not None:
            payload["isTableKeyColumn"] = is_table_key_column

        return self._request("PUT", f"storage/{model_name}/custom-column", data=payload)
