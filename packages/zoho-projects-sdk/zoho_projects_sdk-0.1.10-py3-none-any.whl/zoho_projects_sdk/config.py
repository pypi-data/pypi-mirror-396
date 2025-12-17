"""
Configuration loader for the SDK.
"""

import os
from typing import Optional

from dotenv import load_dotenv


def load_sdk_config() -> None:
    """
    Loads configuration from a .env file and environment variables.
    """
    load_dotenv()


class Settings:
    """
    Holds all settings for the SDK.
    """

    ZOHO_PROJECTS_CLIENT_ID: Optional[str] = os.getenv("ZOHO_PROJECTS_CLIENT_ID")
    ZOHO_PROJECTS_CLIENT_SECRET: Optional[str] = os.getenv(
        "ZOHO_PROJECTS_CLIENT_SECRET"
    )
    ZOHO_PROJECTS_REFRESH_TOKEN: Optional[str] = os.getenv(
        "ZOHO_PROJECTS_REFRESH_TOKEN"
    )
    ZOHO_PROJECTS_PORTAL_ID: Optional[str] = os.getenv("ZOHO_PROJECTS_PORTAL_ID")


# Load the configuration when the module is imported
load_sdk_config()
settings = Settings()
