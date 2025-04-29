import asyncio
import logging

import aiohttp

from fail2banmonitoring.db.config import SqlConnectorConfig, SqlEngine
from fail2banmonitoring.fail2ban.log_parser import Fail2BanLogParser
from fail2banmonitoring.models.ip import IpModel
from fail2banmonitoring.services.ip import IPMetadata
from fail2banmonitoring.utils.environment_variables import EnvironmentVariables

logger = logging.getLogger(__name__)


async def main() -> None:
    """Read Fail2ban logs, enrich IPs with metadata, and store results in the database."""
    try:
        environment_variables = EnvironmentVariables()
        fail2ban_log_parser = Fail2BanLogParser(
            log_path=environment_variables.log_path or "/var/log/fail2ban.log",
            output_file=environment_variables.export_ip_path,
        )
        local_ips = fail2ban_log_parser.read_logs()

        enriched_ips = None
        async with aiohttp.ClientSession() as session:
            if len(local_ips) == 0:
                logger.info("No Ips to fetch")
            elif len(local_ips) == 1:
                enriched_ips = [
                    await IPMetadata.get_ip_metadata(
                        next(iter(local_ips)),
                        session,
                    ),
                ]
            else:
                enriched_ips = await IPMetadata.get_ips_metadata_batch(
                    list(local_ips),
                    session,
                )
        if enriched_ips is not None:
            sql_engine = SqlEngine(
                SqlConnectorConfig(
                    drivername=environment_variables.driver,
                    username=environment_variables.username,
                    password=environment_variables.password,
                    host=environment_variables.host,
                    database=environment_variables.database,
                ),
            )
            await IpModel.create_table(sql_engine)
            await IpModel.insert(
                enriched_ips,
                sql_engine,
            )
    except Exception:
        logger.exception("An unexpected error occurred in the main workflow")


if __name__ == "__main__":
    asyncio.run(main())
