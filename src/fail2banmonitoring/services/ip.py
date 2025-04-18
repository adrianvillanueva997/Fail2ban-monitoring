import asyncio
from enum import Enum
from itertools import batched
from typing import Self

import aiohttp
from pydantic import AliasPath, BaseModel, Field


class _IPAPIRULS(Enum):
    # Unfortunately these endpoints are not HTTPS
    batch = "http://ip-api.com/batch"
    single = "http://ip-api.com/json"


class IPMetadata(BaseModel):
    """Represents metadata information for an IP address as returned by ip-api.com.

    Attributes:
        status (str): The status of the API response.
        country (str): The country name.
        country_code (str): The country code.
        region (str): The region code.
        region_name (str): The region name.
        city (str): The city name.
        zip (str): The postal code.
        lat (float): Latitude.
        lon (float): Longitude.
        timezone (str): Timezone.
        isp (str): Internet service provider.
        org (str): Organization.
        as_ (str): Autonomous system.
        query (str): Queried IP address.

    """

    status: str
    country: str
    country_code: str = Field(validation_alias=AliasPath("CountryCode", 0))
    region: str
    region_name: str = Field(validation_alias=AliasPath("RegionName", 0))
    city: str
    zip: str
    lat: float
    lon: float
    timezone: str
    isp: str
    org: str
    as_: str = Field(validation_alias=AliasPath("as", 0))
    query: str

    @classmethod
    async def get_ips_metadata_batch(
        cls,
        ips: list[str],
        session: aiohttp.ClientSession,
    ) -> list[Self]:
        """Fetch metadata for a list of IP addresses using the ip-api.com batch endpoint.

        This method sends the IPs in batches of up to 100 per request, respecting the free tier
        rate limit of 45 requests per minute. It returns a list of IPMetadata objects
        constructed from the API responses.

        Args:
            ips (list[str]): List of IP addresses to query.
            session (aiohttp.ClientSession): An open aiohttp session for making HTTP requests.

        Returns:
            list[Self]: List of IPMetadata objects with metadata for each IP.

        Raises:
            aiohttp.ClientError: If an HTTP request fails.
            pydantic.ValidationError: If the API response cannot be parsed into IPMetadata.

        """
        ips_metadata: list[Self] = []
        for _request_count, _batch in enumerate(batched(ips, 100), start=1):
            if _request_count % 45 == 0:
                await asyncio.sleep(60)
            try:
                async with session.post(
                    _IPAPIRULS.batch.value,
                    json=_batch,
                ) as response:
                    if response.status != 200:
                        msg = f"Batch request failed with status {response.status}"
                        raise aiohttp.ClientError(msg)  # noqa: TRY301
                    try:
                        batch_json = await response.json()
                    except Exception as e:
                        msg = f"Failed to decode JSON: {e}"
                        raise ValueError(msg)
                    try:
                        ips_metadata.extend(
                            [cls(**_response) for _response in batch_json],
                        )
                    except Exception as e:
                        msg = f"Pydantic validation failed: {e}"
                        raise ValueError(msg)
            except aiohttp.ClientError as e:
                msg = f"HTTP error during batch request: {e}"
                raise aiohttp.ClientError(msg)
        return ips_metadata

    @classmethod
    async def get_ip_metadata(cls, ip: str, session: aiohttp.ClientSession) -> Self:
        """Asynchronously retrieves metadata for a given IP address using the ip-api.com json endpoint.

        This is intended for single IPs not for batch. This method will create a session and will not check
        for limit rates.

        Args:
            ip (str): The IP address to retrieve metadata for.
            session (aiohttp.ClientSession): An open aiohttp session for making HTTP requests.

        Returns:
            Self: IPMetadata object with metadata for the IP.

        Raises:
            aiohttp.ClientError: If there is an issue with the HTTP request.
            ValueError: If the response cannot be parsed as JSON or does not match the expected format.

        Example:
            metadata = await MyClass.get_ip_metadata("8.8.8.8")

        """
        try:
            async with session.get(f"{_IPAPIRULS.single.value}/{ip}") as _response:
                if _response.status != 200:
                    msg = f"Single IP request failed with status {_response.status}"
                    raise aiohttp.ClientError(msg)  # noqa: TRY301
                try:
                    json_response = await _response.json()
                except Exception as e:
                    msg = f"Failed to decode JSON: {e}"
                    raise ValueError(msg)
                try:
                    return cls(**json_response)
                except Exception as e:
                    msg = f"Pydantic validation failed: {e}"
                    raise ValueError(msg)
        except aiohttp.ClientError as e:
            msg = f"HTTP error during single IP request: {e}"
            raise aiohttp.ClientError(msg)
