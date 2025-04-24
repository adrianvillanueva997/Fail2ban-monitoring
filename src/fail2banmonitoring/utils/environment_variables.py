import os
from enum import Enum
from functools import cached_property


# Here we define the environment variables and if they are mandatory or not
class _EnvVar(Enum):
    driver = ("DRIVER", True)  # Database driver
    host = ("HOST", True)  # Database host
    username = ("USERNAME", True)  # Database username
    password = ("PASSWORD", True)
    database = ("DATABASE", True)  # Database name
    log_path = ("LOG_PATH", True)  # Logs to parse
    export_ip_path = ("EXPORT_IP_PATH", False)  # Export fetched ips location


# Here, based on the previous enum we dynamically create the attributes based on the previous enum
class _EnvMeta(type):
    def __new__(cls, name: str, bases: tuple[type, ...], dct: dict) -> type:
        annotations = {}

        for var in _EnvVar:
            key = var.name
            annotations[key] = str | None

            def _getter(v: _EnvVar = var) -> str | None:
                value: str | None = os.getenv(v.value[0])
                if v.value[1] and value is None:
                    msg = f"Missing required env variable: {v.value[0]}"
                    raise OSError(msg)
                return value

            dct[key] = cached_property(_getter)

        dct["__annotations__"] = annotations
        return super().__new__(cls, name, bases, dct)


# My IDE was not smart enough to detect the attributes being dynamically created, so i made an interface on top of it.
# Sadly I have to duplicate the enum values here for typing purposes
class EnvironmentVariables(metaclass=_EnvMeta):
    """Access environment variables as properties, with validation for required ones."""

    driver: str | None
    host: str | None
    username: str | None
    password: str | None
    database: str | None
    log_path: str | None
    export_ip_path: str | None
