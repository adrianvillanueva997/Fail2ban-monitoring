import os
import time
from pathlib import Path
from typing import TYPE_CHECKING

import aiohttp
import anyio
import psycopg2
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from fail2banmonitoring.db.config import SqlConnectorConfig, SqlEngine
from fail2banmonitoring.fail2ban.log_parser import Fail2BanLogParser
from fail2banmonitoring.models.ip import IpModel
from fail2banmonitoring.services.ip import IPMetadata
from fail2banmonitoring.utils.environment_variables import EnvironmentVariables

if TYPE_CHECKING:
    import pathlib


def set_env_vars(tmp_path: Path) -> None:
    os.environ["DRIVER"] = "postgresql+asyncpg"
    os.environ["HOST"] = "127.0.0.1"
    os.environ["PORT"] = "5432"
    os.environ["USERNAME"] = "test"
    os.environ["PASSWORD"] = ""  # Empty password for trust authentication
    os.environ["DATABASE"] = "test"
    os.environ["LOG_PATH"] = str(tmp_path / "fail2ban.log")
    os.environ["EXPORT_IP_PATH"] = str(tmp_path / "banned.txt")


async def prepare_fake_log(log_path: str) -> None:
    async with await anyio.open_file(log_path, "w") as f:
        await f.write(
            "2024-06-01 12:00:00,000 fail2ban.actions        [1234]: NOTICE  [sshd] Ban 8.8.8.8\n",
        )
        await f.flush()


@pytest.mark.asyncio
async def test_end_to_end_postgres(tmp_path: "pathlib.Path") -> None:
    """End-to-end test that parses a fake fail2ban log.

    Enriches IP data, inserts it into the database, and verifies the insertion.
    """
    set_env_vars(tmp_path)
    log_path = os.environ["LOG_PATH"]
    await prepare_fake_log(log_path)

    # Wait for Postgres to be ready (retry loop)
    for _ in range(20):
        try:
            # Try connection with or without password to handle both trust and password auth
            try:
                # First try with password
                conn = psycopg2.connect(
                    host="127.0.0.1",
                    port=5432,
                    user="test",
                    password="test",
                    dbname="test",
                )
            except psycopg2.OperationalError:
                # If that fails, try without password (trust auth)
                conn = psycopg2.connect(
                    host="127.0.0.1",
                    port=5432,
                    user="test",
                    dbname="test",
                )
            conn.close()
            break
        except Exception:
            time.sleep(1)
    else:
        msg = "Postgres service did not become ready in time"
        raise RuntimeError(msg)

    environment_variables = EnvironmentVariables()
    if environment_variables.log_path is None:
        msg = "LOG_PATH environment variable is not set"
        raise ValueError(msg)
    parser = Fail2BanLogParser(
        log_path=environment_variables.log_path,
        output_file=environment_variables.export_ip_path,
    )
    # Create tables
    if environment_variables.port is None:
        msg = "PORT environment variable is not set"
        raise ValueError(msg)
    sql_config = SqlConnectorConfig(
        drivername=environment_variables.driver,
        username=environment_variables.username,
        password=environment_variables.password,
        host=environment_variables.host,
        port=int(environment_variables.port),
        database=environment_variables.database,
    )

    sql_engine = SqlEngine(url_config=sql_config)

    # Print debug info - use double engine to access the actual engine
    print(f"Connection string: {sql_config.url_str}")  # noqa: T201
    print(f"sql_engine.engine type: {type(sql_engine.engine)}")  # noqa: T201

    # Use the correct engine directly - AsyncEngine class
    await IpModel.create_table(sql_engine)

    ips = parser.read_logs()
    assert "8.8.8.8" in ips  # noqa: S101

    async with aiohttp.ClientSession() as session:
        enriched = await IPMetadata.get_ips_metadata_batch(list(ips), session)

    await IpModel.insert(enriched, sql_engine)

    # Fix: Use sql_engine.engine directly for AsyncSession
    async with AsyncSession(sql_engine.engine) as session:
        result = await session.execute(
            text("SELECT ip_address FROM ip WHERE ip_address = '8.8.8.8'"),
        )
        row = result.first()
        assert row is not None, "IP was not inserted into the database"  # noqa: S101
