import os
import pathlib

import aiohttp
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
async def test_end_to_end_sqlite(tmp_path: pathlib.Path) -> None:
    """End-to-end test using SQLite.

    Parses a fake fail2ban log, enriches IP data, inserts it into the database,
    and verifies the insertion.
    """
    # Setup environment variables
    os.environ["DRIVER"] = "sqlite+aiosqlite"
    os.environ["DATABASE"] = str(tmp_path / "test.db")
    os.environ["LOG_PATH"] = str(tmp_path / "fail2ban.log")
    os.environ["EXPORT_IP_PATH"] = str(tmp_path / "banned.txt")

    # Prepare a fake fail2ban log file
    log_path = os.environ["LOG_PATH"]
    async with await anyio.open_file(log_path, "w") as f:
        await f.write(
            "2024-06-01 12:00:00,000 fail2ban.actions        [1234]: NOTICE  [sshd] Ban 8.8.8.8\n",
        )

    # Verify log file was created properly
    assert pathlib.Path(log_path).exists(), f"Log file not created at {log_path}"  # noqa: S101
    async with await anyio.open_file(log_path, "r") as f:
        content = await f.read()
        assert "Ban 8.8.8.8" in content, (  # noqa: S101
            "Log file doesn't contain the expected IP ban entry"
        )
    # Create SQLite database URL for direct table creation
    db_url = f"sqlite+aiosqlite:///{os.environ['DATABASE']}"
    engine = create_async_engine(db_url, echo=True)

    # Create tables using SQLAlchemy
    async with engine.begin() as conn:
        await conn.run_sync(_Base.metadata.create_all)

    # Run the main workflow
    environment_variables = EnvironmentVariables()
    parser = Fail2BanLogParser(
        log_path=environment_variables.log_path or "",
        output_file=environment_variables.export_ip_path or "",
    )
    ips = parser.read_logs()
    assert "8.8.8.8" in ips, f"Expected IP 8.8.8.8 not found in parsed IPs: {ips}"  # noqa: S101

    # Enrich IPs
    async with aiohttp.ClientSession() as session:
        enriched = await IPMetadata.get_ips_metadata_batch(list(ips), session)

    # Create SqlConnectorConfig
    sql_config = SqlConnectorConfig(
        drivername=environment_variables.driver,
        database=environment_variables.database,
    )

    # Use the patched TestSqlEngine
    sql_engine = SqlEngine(url_config=sql_config)
    await IpModel.insert(enriched, sql_engine)

    # Check DB for inserted IP - use a new session with the raw engine
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text("SELECT ip_address FROM ip WHERE ip_address = '8.8.8.8'"),
        )
        row = result.first()
        assert row is not None, "IP was not inserted into the database"  # noqa: S101
