"""
Bedrock Edition Minecraft server status client.

This module provides a client for querying the status of Bedrock Edition Minecraft
servers using the mcstatus.io API. It supports both synchronous and asynchronous
requests.
"""

import requests
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional, Literal

from .constants import (
    BASE_URL,
    DEFAULT_TIMEOUT,
    BedrockPlayers,
    StatusResponse,
    BedrockServerStatusOffline,
    BedrockVersion,
    MOTD,
)

from .exceptions import (
    McstatusioConnectionError,
    McstatusioHTTPError,
    McstatusioTimeoutError,
)

@dataclass(frozen=True)
class BedrockServerStatusResponse(StatusResponse):
    """
    Response data for an online Bedrock Edition Minecraft server.

    Extends StatusResponse with Bedrock Edition-specific information including
    version details, player information, MOTD, gamemode, and edition type.

    Attributes:
        version: Server version information (name and protocol)
        players: Player count (online and max)
        motd: Message of the day (raw, clean, and HTML formats)
        gamemode: Server gamemode (e.g., "Survival", "Creative")
        server_id: Unique server identifier
        edition: Server edition type ("MCPE" for Pocket Edition, "MCEE" for Education Edition)
    """

    version: BedrockVersion
    players: BedrockPlayers
    motd: MOTD
    gamemode: Optional[str]
    server_id: Optional[str]
    edition: Literal["MCPE", "MCEE", None]


class BedrockServer:
    """
    Client for querying Bedrock Edition Minecraft server status.

    This class provides methods to retrieve status information from Bedrock Edition
    Minecraft servers via the mcstatus.io API. Both synchronous and asynchronous
    methods are available.

    Args:
        hostname: Server hostname or IP address. Can include port as "hostname:port"
        port: Server port (default: 19132, the standard Minecraft Bedrock port)
        timeout: Request timeout in seconds (default: 5)

    Attributes:
        hostname: The server hostname or IP address
        port: The server port number
        timeout: Request timeout in seconds

    Example:
        >>> server = BedrockServer("play.cubecraft.net", port=19132)
        >>> status = server.status()
        >>> print(f"Online: {status.online}")
        >>> print(f"Players: {status.players.online}/{status.players.max}")

        >>> # Using async
        >>> import asyncio
        >>> async def get_status():
        ...     server = BedrockServer("play.cubecraft.net")
        ...     status = await server.async_status()
        ...     return status
        >>> asyncio.run(get_status())
    """

    def __init__(
        self, hostname: str, port: int = 19132, timeout: int = DEFAULT_TIMEOUT
    ):
        self.hostname = hostname
        self.port = port
        self.timeout = timeout

    def _parse_hostname(self) -> tuple[str, int]:
        """
        Parse hostname and extract port if specified.

        This method does not modify instance attributes. It extracts
        hostname and port values for use in API requests.

        Returns:
            Tuple of (hostname, port)
        """
        if ":" in self.hostname:
            host_parts = self.hostname.split(":")
            return host_parts[0], int(host_parts[1])
        return self.hostname, self.port

    def _build_response(
        self, data: dict
    ) -> BedrockServerStatusResponse | BedrockServerStatusOffline:
        """
        Build response object from API data.

        Args:
            data: Raw JSON response from the API

        Returns:
            BedrockServerStatusResponse if server is online, otherwise BedrockServerStatusOffline
        """
        if data.get("online"):
            return BedrockServerStatusResponse(
                online=data["online"],
                ip_address=data["ip_address"],
                eula_blocked=data.get("eula_blocked"),
                retrieved_at=data.get("retrieved_at"),
                expiries_at=data.get("expiries_at"),
                port=data["port"],
                version=BedrockVersion(
                    name=data["version"].get("name"),
                    protocol=data["version"].get("protocol"),
                ),
                players=BedrockPlayers(
                    max=data["players"].get("max"), online=data["players"].get("online")
                ),
                motd=MOTD(
                    raw=data["motd"]["raw"],
                    clean=data["motd"]["clean"],
                    html=data["motd"]["html"],
                ),
                gamemode=data.get("gamemode"),
                server_id=data.get("server_id"),
                edition=data.get("edition"),
            )
        else:
            return BedrockServerStatusOffline(
                online=data["online"],
                port=data["port"],
                ip_address=data.get("ip_address"),
                eula_blocked=data.get("eula_blocked", False),
                retrieved_at=data.get("retrieved_at", 0),
                expiries_at=data.get("expiries_at", 0),
            )

    def status(self) -> BedrockServerStatusResponse | BedrockServerStatusOffline:
        """
        Retrieve the server status synchronously.

        Queries the mcstatus.io API to get the current status of the Bedrock Edition
        Minecraft server. If the hostname contains a port (e.g., "example.com:19133"),
        it will be parsed and used instead of the default port.

        Returns:
            BedrockServerStatusResponse if the server is online, containing detailed
            server information including version, players, MOTD, gamemode, and edition.
            BedrockServerStatusOffline if the server is offline, containing basic
            information like port and IP address.

        Raises:
            requests.exceptions.HTTPError: If the API request fails
            requests.exceptions.Timeout: If the request times out
            requests.exceptions.RequestException: For other request-related errors

        Example:
            >>> server = BedrockServer("play.cubecraft.net")
            >>> status = server.status()
            >>> if status.online:
            ...     print(f"Server is online with {status.players.online} players")
            ...     print(f"Edition: {status.edition}")
            ... else:
            ...     print("Server is offline")
        """
        hostname, port = self._parse_hostname()
        url = f"{BASE_URL}/status/bedrock/{hostname}:{port}"
        params = {"timeout": self.timeout}
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            raise McstatusioTimeoutError("Request timed out") from e
        except requests.exceptions.ConnectionError as e:
            raise McstatusioConnectionError("Connection error occurred") from e
        except requests.exceptions.HTTPError as e:
            raise McstatusioHTTPError(
                f"HTTP error occurred: {e.response.status_code}"
            ) from e
        data = response.json()
        return self._build_response(data)

    async def async_status(
        self,
    ) -> BedrockServerStatusResponse | BedrockServerStatusOffline:
        """
        Retrieve the server status asynchronously.

        Asynchronously queries the mcstatus.io API to get the current status of the
        Bedrock Edition Minecraft server. If the hostname contains a port (e.g.,
        "example.com:19133"), it will be parsed and used instead of the default port.

        Returns:
            BedrockServerStatusResponse if the server is online, containing detailed
            server information including version, players, MOTD, gamemode, and edition.
            BedrockServerStatusOffline if the server is offline, containing basic
            information like port and IP address.

        Raises:
            aiohttp.ClientError: If the API request fails
            asyncio.TimeoutError: If the request times out
            aiohttp.ClientResponseError: For HTTP error responses

        Example:
            >>> import asyncio
            >>> async def check_server():
            ...     server = BedrockServer("play.cubecraft.net")
            ...     status = await server.async_status()
            ...     if status.online:
            ...         print(f"Server is online with {status.players.online} players")
            ...         print(f"Edition: {status.edition}")
            ...     else:
            ...         print("Server is offline")
            >>> asyncio.run(check_server())
        """
        hostname, port = self._parse_hostname()
        url = f"{BASE_URL}/status/bedrock/{hostname}:{port}"
        params = {"timeout": self.timeout}
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
        except asyncio.TimeoutError as e:
            raise McstatusioTimeoutError("Request timed out") from e
        except aiohttp.ClientConnectionError as e:
            raise McstatusioConnectionError("Connection error occurred") from e
        except aiohttp.ClientResponseError as e:
            raise McstatusioHTTPError(
                f"HTTP error occurred: {e.status}"
            ) from e
        return self._build_response(data)
