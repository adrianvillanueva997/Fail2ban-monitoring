import os

import anyio
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fail2banmonitoring.db.config import SqlConnectorConfig, SqlEngine
from fail2banmonitoring.fail2ban.log_parser import Fail2BanLogParser
from fail2banmonitoring.models.base import _Base
from fail2banmonitoring.models.ip import IpModel
from fail2banmonitoring.services.ip import IPMetadata
from fail2banmonitoring.utils.environment_variables import EnvironmentVariables


@pytest.mark.asyncio
async def test_end_to_end_sqlite(tmp_path) -> None:
    """End-to-end test for the SQLite workflow: parses a fake fail2ban log, enriches IPs, inserts them into the database, and verifies insertion."""
    # Use a temporary SQLite file
    db_path = tmp_path / "test.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"
    os.environ["DRIVER"] = "sqlite+aiosqlite"
    os.environ["HOST"] = ""
    os.environ["USERNAME"] = ""
    os.environ["PASSWORD"] = ""
    os.environ["DATABASE"] = str(db_path)
    os.environ["LOG_PATH"] = str(tmp_path / "fail2ban.log")
    os.environ["EXPORT_IP_PATH"] = str(tmp_path / "banned.txt")

    # Prepare a fake fail2ban log file

    async with await anyio.open_file(os.environ["LOG_PATH"], "w") as f:
        await f.write(
            "2024-06-01 12:00:00,000 fail2ban.actions        [1234]: NOTICE  [sshd] Ban 8.8.8.8\n",
        )

    # Create tables
    engine = create_async_engine(db_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(_Base.metadata.create_all)

    # Run the main workflow: parse log, enrich, insert
    environment_variables = EnvironmentVariables()
    parser = Fail2BanLogParser(
        log_path=environment_variables.log_path or "",
        output_file=environment_variables.export_ip_path or "",
    )
    ips = parser.read_logs()
    assert "8.8.8.8" in ips  # noqa: S101

    # Enrich IPs
    import aiohttp

    async with aiohttp.ClientSession() as session:
        enriched = await IPMetadata.get_ips_metadata_batch(list(ips), session)

    # Insert into DB
    await IpModel.insert(
        enriched,
        SqlEngine(
            SqlConnectorConfig(
                drivername=environment_variables.driver,  # type: ignore
                username=environment_variables.username,  # type: ignore
                password=environment_variables.password,  # type: ignore
                host=environment_variables.host,  # type: ignore
                database=environment_variables.database,  # type: ignore
            ),
        ),
    )

    # Check DB for inserted IP
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text("SELECT query FROM ip WHERE query = '8.8.8.8'"),
        )
        row = result.first()
        assert row is not None, "IP was not inserted into the database"  # noqa: S101
