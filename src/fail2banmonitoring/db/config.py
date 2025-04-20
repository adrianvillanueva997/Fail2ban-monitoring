from dataclasses import dataclass
from functools import cached_property

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine


@dataclass
class SqlConnectorConfig:
    """Dataclass to manage SqlAlchemy connector configurations."""

    drivername: str
    username: str
    password: str
    host: str
    database: str

    @cached_property
    def url(self) -> URL:
        """Return a SQLAlchemy URL object using the connector configuration."""
        return URL.create(
            drivername=self.drivername,
            username=self.username,
            password=self.password,
            host=self.host,
            database=self.database,
        )

    @cached_property
    def url_str(self) -> str:
        """Return the string representation of the SQLAlchemy URL object."""
        return str(self.url)

    def __post_init__(self) -> None:
        """Validate the drivername to ensure it is an accepted async driver."""
        valid_async_drivers = {
            "postgresql+asyncpg",
            "mysql+aiomysql",
            "mysql+asyncmy",
        }
        if self.drivername not in valid_async_drivers:
            msg = (
                f"Invalid or unsupported async driver '{self.drivername}'. "
                f"Supported drivers: {', '.join(valid_async_drivers)}."
            )
            raise ValueError(
                msg,
            )


@dataclass
class SqlEngine:
    """Class to manage the creation of an asynchronous SQLAlchemy engine using the provided connector configuration."""

    url_config: SqlConnectorConfig
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 5

    @cached_property
    def engine(
        self,
    ) -> AsyncEngine:
        """Create and return an asynchronous SQLAlchemy engine using the provided configuration."""
        return create_async_engine(
            self.url_config.url_str,
            echo=self.echo,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
        )
