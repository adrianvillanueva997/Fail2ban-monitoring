import logging
from datetime import datetime
from typing import Self

import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
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
    country : str | None
        The country of the IP address.
    country_code : str | None
        The country code of the IP address.
    region : str | None
        The region of the IP address.
    region_name : str | None
        The name of the region of the IP address.
    city : str | None
        The city of the IP address.
    zip : str | None
        The ZIP code of the IP address.
    lat : float | None
        The latitude of the IP address.
    lon : float | None
        The longitude of the IP address.
    timezone : str | None
        The timezone of the IP address.
    isp : str | None
        The ISP of the IP address.
    org : str | None
        The organization of the IP address.
    as_field : str | None
        The autonomous system (AS) of the IP address.
    ip_address : str | None
        The IP address.
    created_at : datetime
        The timestamp when the record was created.

    Methods
    -------
    insert(ips: List[IPMetadata], sql_engine: SqlEngine) -> None
        Insert a list of IPMetadata objects into the database.

    """

    __tablename__ = "ip"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    country: Mapped[str | None] = mapped_column(sa.String(30))
    country_code: Mapped[str | None] = mapped_column(sa.String(30))
    region: Mapped[str | None] = mapped_column(sa.String(30))
    region_name: Mapped[str | None] = mapped_column(sa.String(30))
    city: Mapped[str | None] = mapped_column(sa.String(30))
    zip: Mapped[str | None] = mapped_column(sa.String(30))
    lat: Mapped[float | None] = mapped_column(sa.Float)
    lon: Mapped[float | None] = mapped_column(sa.Float)
    timezone: Mapped[str | None] = mapped_column(sa.String(50))
    isp: Mapped[str | None] = mapped_column(sa.String(50))
    org: Mapped[str | None] = mapped_column(sa.String(50))
    as_field: Mapped[str | None] = mapped_column("as", sa.String(50), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(sa.String(50), name="query")
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime,
        server_default=sa.func.now(),
    )

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
            as_field=ip_metadata.as_value,
            ip_address=ip_metadata.query,
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
        """Insert a list of IPMetadata objects into the database efficiently using bulk insert.

        Parameters
        ----------
        ips : List[IPMetadata]
            The list of IPMetadata objects to be inserted.
        sql_engine : SqlEngine
            The SQLAlchemy engine instance used for database operations.

        Raises
        ------
        SQLAlchemyError
            If a database error occurs that cannot be resolved with retries
        ValueError
            If there's an issue with the data format or the engine is not initialized

        """
        if not ips:
            logger.debug("No IP records to insert")
            return

        try:
            ip_models = [IpModel.from_metadata(ip) for ip in ips]

            try:
                engine = sql_engine.engine.engine
            except Exception as e:
                logger.exception("Failed to initialize database engine: %s")
                msg = f"Database engine initialization failed: {e!s}"
                raise ValueError(msg) from e
            try:
                async with AsyncSession(engine) as session, session.begin():
                    session.add_all(ip_models)
                logger.debug("Bulk inserted %d IP records into the database", len(ips))
            except SQLAlchemyError as e:
                logger.exception("Database error during bulk insert: %s")
                raise
        except Exception as e:
            logger.exception("Failed to insert IP records: %s")
            raise
