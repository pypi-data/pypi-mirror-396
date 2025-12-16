"""
Cloud Amplifier Utility Functions

This module contains utility functions for Cloud Amplifier operations.
"""

from typing import Literal

__all__ = [
    "ENGINES",
    "create_integration_body",
]

# TODO: Expand to include all engines
ENGINES = Literal["SNOWFLAKE", "BIGQUERY"]


def create_integration_body(
    engine: ENGINES,
    description: str,
    friendly_name: str,
    service_account_id: str,
    auth_method: str,
    admin_auth_method: str,
):
    body = {
        "engine": engine,
        "properties": {
            "friendlyName": {
                "key": "friendlyName",
                "configType": "CONFIG",
                "value": friendly_name,
            },
            "description": {
                "key": "description",
                "configType": "CONFIG",
                "value": description,
            },
            "serviceAccountId": {
                "key": "serviceAccountId",
                "configType": "CONFIG",
                "value": service_account_id,
            },
            "AUTH_METHOD": {
                "key": "AUTH_METHOD",
                "configType": "CONFIG",
                "value": auth_method,
            },
            "ADMIN_AUTH_METHOD": {
                "key": "ADMIN_AUTH_METHOD",
                "configType": "CONFIG",
                "value": admin_auth_method,
            },
        },
    }
    return body
