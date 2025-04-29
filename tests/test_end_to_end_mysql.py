import os  # noqa: INP001
from pathlib import Path

import aiohttp
import anyio
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.mysql import MySqlContainer

from fail2banmonitoring.db.config import SqlConnectorConfig, SqlEngine
from fail2banmonitoring.fail2ban.log_parser import Fail2BanLogParser
from fail2banmonitoring.models.base import _Base
from fail2banmonitoring.models.ip import IpModel
from fail2banmonitoring.services.ip import IPMetadata
from fail2banmonitoring.utils.environment_variables import EnvironmentVariables


def set_env_vars(mysql, tmp_path) -> None:
    os.environ["DRIVER"] = "mysql+aiomysql"
    os.environ["HOST"] = mysql.get_container_host_ip()
    os.environ["USERNAME"] = mysql.username
    os.environ["PASSWORD"] = mysql.password
    os.environ["DATABASE"] = mysql.dbname
    os.environ["LOG_PATH"] = str(tmp_path / "fail2ban.log")
    os.environ["EXPORT_IP_PATH"] = str(tmp_path / "banned.txt")


def prepare_fake_log(log_path):
    async def _write() -> None:
        async with await anyio.open_file(log_path, "w") as f:
            await f.write(
                "2024-06-01 12:00:00,000 fail2ban.actions        [1234]: NOTICE  [sshd] Ban 8.8.8.8\n",
            )
            # Ensure data is flushed to disk
            await f.flush()
        if Path(log_path).exists():
            async with await anyio.open_file(log_path, "r") as f:
                content = await f.read()
                content = await f.read()

    return _write()


@pytest.mark.asyncio
async def test_end_to_end_mysql(tmp_path) -> None:
    with MySqlContainer("mysql:8.0") as mysql:
        set_env_vars(mysql, tmp_path)
        log_path = os.environ["LOG_PATH"]
        await prepare_fake_log(log_path)

        # Create tables
        db_url = mysql.get_connection_url().replace("mysql://", "mysql+aiomysql://")
        engine = create_async_engine(db_url, echo=True)
        async with engine.begin() as conn:
            await conn.run_sync(_Base.metadata.create_all)

        environment_variables = EnvironmentVariables()
        if environment_variables.log_path is None:
            msg = "LOG_PATH environment variable is not set"
            raise ValueError(msg)
        parser = Fail2BanLogParser(
            log_path=environment_variables.log_path,
            output_file=environment_variables.export_ip_path,
        )

        ips = parser.read_logs()
        assert "8.8.8.8" in ips  # noqa: S101

        async with aiohttp.ClientSession() as session:
            enriched = await IPMetadata.get_ips_metadata_batch(list(ips), session)

        sql_config = SqlConnectorConfig(
            drivername=environment_variables.driver,
            username=environment_variables.username,
            password=environment_variables.password,
            host=environment_variables.host,
            port=int(mysql.port),
            database=environment_variables.database,
        )

        sql_engine = SqlEngine(url_config=sql_config)
        await IpModel.insert(enriched, sql_engine)

        # Check DB for inserted IP - use column name ip_address
        async with AsyncSession(engine) as session:
            result = await session.execute(
                text("SELECT ip_address FROM ip WHERE ip_address = '8.8.8.8'"),
            )
            row = result.first()
            assert row is not None, "IP was not inserted into the database"  # noqa: S101
