import os
from functools import cached_property
from typing import ClassVar


class EnvironmentVariables:
    """Access environment variables as properties, with validation for required ones."""

    # Define environment variables as (env_var_name, is_required)
    ENV_VARS: ClassVar[dict[str, tuple[str, bool]]] = {
        "driver": ("DRIVER", True),
        "host": ("HOST", True),
        "username": ("USERNAME", True),
        "password": ("PASSWORD", True),
        "database": ("DATABASE", True),
        "log_path": ("LOG_PATH", True),  # Changed to required
        "export_ip_path": ("EXPORT_IP_PATH", False),
        "port": ("PORT", False),
    }

    def __init_subclass__(cls) -> None:
        """Validate that subclasses don't override property methods."""
        for var_name in cls.ENV_VARS:
            if var_name in cls.__dict__:
                msg = f"Cannot override {var_name} property in {cls.__name__}"
                raise TypeError(msg)

    def __getattr__(self, name: str) -> str | None:
        """Handle dynamic property access for environment variables not explicitly defined."""
        if name in self.ENV_VARS:
            return self._get_env_var(name)
        msg = f"{self.__class__.__name__} has no attribute '{name}'"
        raise AttributeError(msg)

    def _get_env_var(self, name: str) -> str | None:
        """Get environment variable value with validation."""
        env_name, required = self.ENV_VARS[name]
        value = os.getenv(env_name)

        if required and value is None:
            msg = f"Missing required environment variable: {env_name}"
            raise OSError(msg)

        # Debug print for environment variable access

        return value

    # Define properties for better IDE support and type checking
    @cached_property
    def driver(self) -> str:
        """Return the value of the DRIVER environment variable."""
        return self._get_env_var("driver") or ""

    @cached_property
    def host(self) -> str:
        """Return the value of the HOST environment variable."""
        return self._get_env_var("host") or ""

    @cached_property
    def username(self) -> str:
        """Return the value of the USERNAME environment variable."""
        return self._get_env_var("username") or ""

    @cached_property
    def password(self) -> str:
        """Return the value of the PASSWORD environment variable."""
        return self._get_env_var("password") or ""

    @cached_property
    def database(self) -> str:
        """Return the value of the DATABASE environment variable."""
        return self._get_env_var("database") or ""

    @cached_property
    def log_path(self) -> str:
        """Return the value of the LOG_PATH environment variable."""
        return self._get_env_var("log_path") or ""

    @cached_property
    def export_ip_path(self) -> str | None:
        """Return the value of the EXPORT_IP_PATH environment variable, or None if not set."""
        return self._get_env_var("export_ip_path")

    @cached_property
    def port(self) -> str | None:
        """Return the value of the Port environment variable, or None if not set."""
        return self._get_env_var("port") or ""
