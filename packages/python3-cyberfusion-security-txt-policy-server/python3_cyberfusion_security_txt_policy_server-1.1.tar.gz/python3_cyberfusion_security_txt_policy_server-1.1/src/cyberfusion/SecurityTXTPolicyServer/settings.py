"""Settings for security-txt-policy-server."""

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

config = Config()

# App

APP_NAME = config("APP_NAME", default="security-txt-policy-server")

# Server

LISTEN_HOST = config("LISTEN_HOST", default="::1")
LISTEN_PORT = config("LISTEN_PORT", cast=int, default=8080)

TRUSTED_PROXY_ADDRESSES = config(
    "TRUSTED_PROXY_ADDRESSES", cast=CommaSeparatedStrings, default="::1"
)

# Database

DATABASE_PATH = config("DATABASE_PATH")
