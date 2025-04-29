import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Literal

import aiohttp
from pydantic import BaseModel, Field, ValidationError, field_validator

logger = logging.getLogger(__name__)


class _IPAPIRules(Enum):
    # Unfortunately these endpoints are not HTTPS
    batch = "http://ip-api.com/batch"
    single = "http://ip-api.com/json"


class IPMetadata(BaseModel):
    """IP Metadata model."""

    # Class variable to store the API URL
    API_URL: ClassVar[str] = "http://ip-api.com/batch"

    status: Literal["success", "fail"]
    query: str

    country: str | None = Field(default=None, alias="country")
    country_code: str | None = Field(default=None, alias="countryCode")
    region: str | None = Field(default=None, alias="region")
    region_name: str | None = Field(default=None, alias="regionName")
    city: str | None = Field(default=None, alias="city")
    zip: str | None = Field(default=None, alias="zip")
    lat: float | None = Field(default=None, alias="lat")
    lon: float | None = Field(default=None, alias="lon")
    timezone: str | None = Field(default=None, alias="timezone")
    isp: str | None = Field(default=None, alias="isp")
    org: str | None = Field(default=None, alias="org")
    as_value: str | None = Field(default=None, alias="as")

    # Fail field
    message: str | None = None

    # Timestamp when this data was retrieved
    fetched_at: datetime = Field(default_factory=datetime.now)

    @field_validator("as_value", mode="before")
    @classmethod
    def validate_as(cls, v: str | None) -> str | None:
        """Validate the 'as' field which is a reserved keyword in Python."""
        return v

    @classmethod
    async def get_ip_metadata(
        cls,
        ip: str,
        session: aiohttp.ClientSession,
    ) -> "IPMetadata":
        """Get metadata for a single IP address."""
        try:
            batch_result = await cls.get_ips_metadata_batch([ip], session)
            if batch_result and len(batch_result) > 0:
                return batch_result[0]
            msg = f"Failed to get metadata for IP {ip}"
            raise ValueError(msg)  # noqa: TRY301
        except Exception as e:
            logger.exception("Error getting metadata for IP %s:", ip)
            raise

    @classmethod
    async def get_ips_metadata_batch(
        cls,
        ips: list[str],
        session: aiohttp.ClientSession,
    ) -> list["IPMetadata"]:
        """Get metadata for a batch of IP addresses."""
        try:
            logger.info("Fetching metadata for %d IPs", len(ips))

            data = [{"query": ip} for ip in ips]

            async with session.post(cls.API_URL, json=data) as response:
                if response.status != 200:
                    text = await response.text()
                    msg = f"API request failed with status {response.status}: {text}"
                    raise ValueError(msg)  # noqa: TRY301

                batch_json = await response.json()
                logger.debug("API response: %s", json.dumps(batch_json))

                # Create models from response
                result = []
                for item in batch_json:
                    try:
                        # Fix field names if needed
                        if "as" in item:
                            item["as_value"] = item.pop("as")

                        # Create model instance
                        result.append(cls(**item))
                    except ValidationError as e:
                        logger.exception("Validation error for item %r", item)
                        # Create a basic instance with error information
                        result.append(
                            cls(
                                status="fail",
                                query=item.get("query", "unknown"),
                                message=f"Validation error: {e}",
                            ),
                        )

                return result
        except Exception as e:
            logger.exception("Error in batch IP metadata request: %r")
            raise

    def to_dict(self) -> dict[str, Any]:
        """Convert the model to a dictionary."""
        return self.model_dump()
