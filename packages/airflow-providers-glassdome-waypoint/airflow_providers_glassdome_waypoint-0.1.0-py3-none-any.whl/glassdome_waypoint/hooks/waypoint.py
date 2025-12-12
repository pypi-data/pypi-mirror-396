from __future__ import annotations

from typing import Any

from airflow.exceptions import AirflowException
from airflow.providers.common.compat.sdk import BaseHook
from glassdome_waypoint_sdk import ApiKeyAuth, WaypointClient, WaypointConfig


class WaypointHook(BaseHook):
    """
    Hook for interacting with Glassdome Waypoint via the Python SDK.
    """

    conn_name_attr: str = "glassdome_waypoint_conn_id"
    default_conn_name: str = "glassdome_waypoint_default"
    conn_type: str = "glassdome-waypoint"
    hook_name: str = "Glassdome Waypoint"

    def __init__(
        self,
        glassdome_waypoint_conn_id: str = default_conn_name,
        logger_name: str | None = None,
    ):
        super().__init__(logger_name=logger_name)
        self.conn_id = glassdome_waypoint_conn_id

    @classmethod
    def get_connection_form_widgets(cls) -> dict[str, Any]:
        """Returns connection widgets to add to connection form"""
        from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
        from flask_babel import lazy_gettext
        from wtforms import StringField

        return {
            "timeout_seconds": StringField(
                label=lazy_gettext("Timeout Seconds"),  # type: ignore
                widget=BS3TextFieldWidget(),
                description="Request timeout in seconds",
            )
        }

    @classmethod
    def get_ui_field_behaviour(cls) -> dict[str, Any]:
        """Returns custom field behaviour"""
        return {
            "hidden_fields": [
                "port",
                "schema",
                "extra",
            ],
            "relabeling": {
                "host": "Base URL",
                "login": "Auth Type",
                "password": "API Key",
            },
            "placeholders": {
                "login": "Supported: api_key",
            },
        }

    def get_conn(self) -> WaypointClient:
        """
        Return an initialized WaypointClient for this connection.
        """

        # Backward compatible way to get the connection
        try:
            conn = self.get_connection(self.conn_id)
        except Exception as e:
            try:
                from airflow.models.connection import Connection

                conn = Connection.get_connection_from_secrets(self.conn_id)
            except Exception:
                raise e

        extra = conn.extra_dejson

        base_url = conn.host
        if not base_url:
            raise AirflowException("Base URL is required")

        config = WaypointConfig(base_url=base_url)
        timeout_seconds = extra.get("timeout_seconds")
        if timeout_seconds:
            try:
                config.timeout_seconds = float(timeout_seconds)
            except ValueError:
                raise AirflowException(
                    f"Timeout seconds must be a number: {timeout_seconds!r}"
                )

        auth_type = conn.login
        if not auth_type:
            raise AirflowException("Auth type is required")

        if auth_type == "api_key":
            api_key = conn.password
            if not api_key:
                raise AirflowException("API key is required for auth_type=api_key")
            auth = ApiKeyAuth(api_key=api_key)
        else:
            raise AirflowException(f"Unsupported auth type: {auth_type!r}")

        return WaypointClient(config=config, auth=auth)

    def get_client(self) -> WaypointClient:
        """
        Return an initialized WaypointClient for this connection.
        """
        return self.get_conn()

    def test_connection(self) -> tuple[bool, str]:
        """
        Used by the "Test" button in the Connection UI.

        We call a cheap, read-only API to verify connectivity & auth.

        Warning: This feature won’t be available for the connections residing in
        external secrets backends when using the Airflow UI or REST API.
        """
        try:
            client = self.get_conn()
            client.operation.list_operations(page_size=1)
            return True, "Successfully connected to the Waypoint API"
        except Exception as e:
            return False, f"Unable to connect to the Waypoint API: {e!r}"
