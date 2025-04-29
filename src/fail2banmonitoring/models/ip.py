import logging
from typing import Self

from sqlalchemy import Double, Integer, String
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
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
    timezone : str
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
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country: Mapped[str] = mapped_column(String(30))
    country_code: Mapped[str] = mapped_column(String(30))
    region: Mapped[str] = mapped_column(String(30))
    region_name: Mapped[str] = mapped_column(String(30))
    city: Mapped[str] = mapped_column(String(30))
    zip: Mapped[str] = mapped_column(String(30))
    lat: Mapped[float] = mapped_column(Double)
    lon: Mapped[float] = mapped_column(Double)
    timezone: Mapped[str] = mapped_column(String(50))
    isp: Mapped[str] = mapped_column(String(50))
    org: MappedColumn[str] = mapped_column(String(50))
    _as: Mapped[str] = mapped_column(String(50), name="as")
    query: Mapped[str] = mapped_column(String(50), name="ip_address")

    @classmethod
    def from_metadata(cls, ip_metadata: IPMetadata) -> Self:
        """Create an IpModel instance from an IPMetadata object."""
        return cls(
            country=ip_metadata.country,
            country_code=ip_metadata.country_code,
            region=ip_metadata.region,
            region_name=ip_metadata.region_name,
            city=ip_metadata.city,
            zip=ip_metadata.zip,
            lat=ip_metadata.lat,
            lon=ip_metadata.lon,
            timezone=ip_metadata.timezone,
            isp=ip_metadata.isp,
            org=ip_metadata.org,
            _as=ip_metadata.as_value,
        )

    @classmethod
    async def create_table(cls, sql_engine: SqlEngine) -> None:
        """Create the IP table in the database if it does not exist."""
        engine = sql_engine.engine
        if isinstance(engine, AsyncEngine):
            async with engine.begin() as conn:
                await conn.run_sync(cls.metadata.create_all)
        else:
            cls.metadata.create_all(bind=engine)

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Initialize subclass; allows for custom subclass initialization."""
        super().__init_subclass__(**kwargs)

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
    @staticmethod
    async def insert(ips: list[IPMetadata], sql_engine: SqlEngine) -> None:
        """Insert a list of IPMetadata objects into the database.

        Parameters
        ----------
        ips : list[IPMetadata]
            The list of IPMetadata objects to be inserted.
        sql_engine : SqlEngine
            The SQLAlchemy engine instance used for database operations.

        """
        ip_models = [IpModel.from_metadata(ip) for ip in ips]
        async with AsyncSession(sql_engine.engine) as session, session.begin():
            try:
                session.add_all(ip_models)
                logger.debug("Inserted %d IP records into the database.", len(ips))
            except Exception:
                await session.rollback()
                logger.exception("Exception occurred during IP insertion.")
                raise
