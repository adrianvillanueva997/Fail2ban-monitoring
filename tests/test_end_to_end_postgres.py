import os
from typing import TYPE_CHECKING

import aiohttp
import anyio
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from fail2banmonitoring.db.config import SqlConnectorConfig, SqlEngine
from fail2banmonitoring.fail2ban.log_parser import Fail2BanLogParser
from fail2banmonitoring.models.base import _Base
from fail2banmonitoring.models.ip import IpModel
from fail2banmonitoring.services.ip import IPMetadata
from fail2banmonitoring.utils.environment_variables import EnvironmentVariables

if TYPE_CHECKING:
    import pathlib


@pytest.mark.asyncio
async def test_end_to_end_postgres(tmp_path: "pathlib.Path") -> None:
    """End-to-end test that starts a PostgreSQL container, parses a fake fail2ban log.

    Enriches IP data, inserts it into the database, and verifies the insertion.
    """
    try:
        import asyncpg  # type: ignore # noqa: F401
    except ImportError:
        pytest.skip("asyncpg is not installed, skipping PostgreSQL test")

    # Start a PostgreSQL container
    with PostgresContainer("postgres:17") as postgres:
        # Setup environment variables
        os.environ["DRIVER"] = "postgresql+asyncpg"
        os.environ["HOST"] = postgres.get_container_host_ip()
        os.environ["PORT"] = str(postgres.port)
        os.environ["USERNAME"] = postgres.username
        os.environ["PASSWORD"] = postgres.password
        os.environ["DATABASE"] = postgres.dbname
        os.environ["LOG_PATH"] = str(tmp_path / "fail2ban.log")
        os.environ["EXPORT_IP_PATH"] = str(tmp_path / "banned.txt")

        # Prepare a fake fail2ban log file
        async with await anyio.open_file(os.environ["LOG_PATH"], "w") as f:
            await f.write(
                "2024-06-01 12:00:00,000 fail2ban.actions        [1234]: NOTICE  [sshd] Ban 8.8.8.8\n",
            )
            await f.flush()

        # Create database URL for asyncpg
        db_url = postgres.get_connection_url().replace(
            "postgresql://",
            "postgresql+asyncpg://",
        )

        # Create tables using SQLAlchemy
        engine = create_async_engine(db_url, echo=True)
        async with engine.begin() as conn:
            await conn.run_sync(_Base.metadata.create_all)

        # Run the main workflow
        environment_variables = EnvironmentVariables()
        parser = Fail2BanLogParser(
            log_path=environment_variables.log_path,
            output_file=environment_variables.export_ip_path,
        )
        ips = parser.read_logs()
        assert "8.8.8.8" in ips  # noqa: S101

        # Enrich IPs
        async with aiohttp.ClientSession() as session:
            enriched = await IPMetadata.get_ips_metadata_batch(list(ips), session)

        # Create SqlConnectorConfig explicitly with port
        sql_config = SqlConnectorConfig(
            drivername=environment_variables.driver,
            username=environment_variables.username,
            password=environment_variables.password,
            host=environment_variables.host,
            port=int(os.environ["PORT"]),  # Explicitly include port
            database=environment_variables.database,
        )

        # Insert using SqlEngine
        sql_engine = SqlEngine(url_config=sql_config)
        await IpModel.insert(enriched, sql_engine)

        # Check DB for inserted IP
        async with AsyncSession(engine) as session:
            result = await session.execute(
                text("SELECT query FROM ip WHERE query = '8.8.8.8'"),
            )
            row = result.first()
            assert row is not None, "IP was not inserted into the database"  # noqa: S101
