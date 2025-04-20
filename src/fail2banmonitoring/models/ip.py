import logging

from sqlalchemy import DateTime, Double, String
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.properties import MappedColumn
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from fail2banmonitoring.db.config import SqlEngine
from fail2banmonitoring.models.base import _Base
from fail2banmonitoring.services.ip import IPMetadata

logger = logging.getLogger(__name__)


class IpModel(_Base):
    """Represents an IP address entry in the database with associated metadata.

    Attributes
    ----------
    country : str
        The country of the IP address.
    country_code : str
        The country code of the IP address.
    region : str
        The region of the IP address.
    region_name : str
        The name of the region of the IP address.
    city : str
        The city of the IP address.
    zip : str
        The ZIP code of the IP address.
    lat : float
        The latitude of the IP address.
    lon : float
        The longitude of the IP address.
    timezone : datetime
        The timezone of the IP address.
    isp : str
        The ISP of the IP address.
    org : str
        The organization of the IP address.
    _as : str
        The autonomous system (AS) of the IP address.

    Methods
    -------
    insert(ips: list[IPMetadata]) -> None
        Insert a list of IPMetadata objects into the database.

    """

    __tablename__ = "ip"
    country: Mapped[str] = mapped_column(String(30))
    country_code: Mapped[str] = mapped_column(String(30))
    region: Mapped[str] = mapped_column(String(30))
    region_name: Mapped[str] = mapped_column(String(30))
    city: Mapped[str] = mapped_column(String(30))
    zip: Mapped[str] = mapped_column(String(30))
    lat: Mapped[float] = mapped_column(Double)
    lon: Mapped[float] = mapped_column(Double)
    timezone: Mapped[datetime] = mapped_column(DateTime())
    isp: Mapped[str] = mapped_column(String(50))
    org: MappedColumn[str] = mapped_column(String(50))
    _as: Mapped[str] = mapped_column(String(50), name="as")

    def __init__(self, engine: SqlEngine) -> None:
        """Initialize the IpModel with a given SQL engine.

        Parameters
        ----------
        engine : SqlEngine
            The SQL engine to be used for database operations.

        """
        self.sql_engine = engine

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(
            multiplier=1,
            min=2,
            max=10,
        ),
        retry=retry_if_exception_type((OperationalError, DBAPIError)),
    )
    async def insert(self, ips: list[IPMetadata]) -> None:
        """Insert a list of IPMetadata objects into the database.

        Parameters
        ----------
        ips : list[IPMetadata]
            The list of IPMetadata objects to be inserted.

        """
        async with AsyncSession(self.sql_engine.engine) as session, session.begin():
            try:
                session.add_all(ips)
                logger.debug("Inserted %d IP records into the database.", len(ips))
            except Exception:
                logger.exception("Exception occurred during IP insertion.")
                raise
