import logging
from dataclasses import dataclass
from functools import cached_property

from sqlalchemy import URL, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)


@dataclass
class SqlConnectorConfig:
    """Dataclass to manage SqlAlchemy connector configurations."""

    drivername: str
    database: str
    username: str | None = None
    password: str | None = None
    host: str | None = None
    port: int | None = None

    @cached_property
    def url(self) -> URL:
        """Return a SQLAlchemy URL object using the connector configuration."""
        if self.drivername == "sqlite+aiosqlite":
            # Special handling for SQLite connection URLs
            return URL.create(
                drivername=self.drivername,
                database=self.database,
            )
        # For other database types, all parameters are required
        if not all([self.username, self.password, self.host, self.port]):
            msg = f"Username, password, and host are required for {self.drivername}"
            raise ValueError(msg)

        return URL.create(
            drivername=self.drivername,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
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
            "sqlite+aiosqlite",
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
        # SQLite doesn't use pool_size and max_overflow
        if self.url_config.drivername == "sqlite+aiosqlite":
            return create_async_engine(
                self.url_config.url_str,
                echo=self.echo,
            )
        # For other database types
        return create_async_engine(
            self.url_config.url_str,
            echo=self.echo,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
        )

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_fixed(3),
        retry=retry_if_exception_type(OperationalError),
    )
    async def ping(self) -> None:
        """Test the connection to the database with retries."""
        async with self.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.debug("Database connection successful.")
