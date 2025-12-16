"""
Java Edition Minecraft server status client.

This module provides a client for querying the status of Java Edition Minecraft
servers using the mcstatus.io API. It supports both synchronous and asynchronous
requests.
"""

import requests
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional
from .constants import (
    BASE_URL,
    DEFAULT_TIMEOUT,
    JavaPlayers,
    StatusResponse,
    JavaServerStatusOffline,
    JavaVersion,
    JavaVersionName,
    MOTD,
    JavaMods,
    JavaPlugins,
    JavaSRV,
)

from .exceptions import (
    McstatusioConnectionError,
    McstatusioHTTPError,
    McstatusioTimeoutError,
)

@dataclass(frozen=True)
class JavaServerStatusResponse(StatusResponse):
    """
    Response data for an online Java Edition Minecraft server.

    Extends StatusResponse with Java Edition-specific information including
    version details, player information, MOTD, server mods/plugins, and more.

    Attributes:
        version: Server version information (name and protocol)
        players: Player count and sample list
        hostname: Server hostname
        motd: Message of the day (raw, clean, and HTML formats)
        icon: Base64-encoded server icon (if available)
        mods: List of installed mods (if available)
        software: Server software name (e.g., "Paper", "Spigot")
        plugins: List of installed plugins (if available)
        srv: SRV record information (if available)
    """

    version: JavaVersion
    players: JavaPlayers
    hostname: str
    motd: MOTD
    icon: Optional[str]
    mods: list[JavaMods] | None
    software: Optional[str]
    plugins: list[JavaPlugins] | None
    srv: JavaSRV | None


class JavaServer:
    """
    Client for querying Java Edition Minecraft server status.

    This class provides methods to retrieve status information from Java Edition
    Minecraft servers via the mcstatus.io API. Both synchronous and asynchronous
    methods are available.

    Args:
        hostname: Server hostname or IP address. Can include port as "hostname:port"
        port: Server port (default: 25565, the standard Minecraft Java port)
        timeout: Request timeout in seconds (default: 5)

    Attributes:
        hostname: The server hostname or IP address
        port: The server port number
        timeout: Request timeout in seconds

    Example:
        >>> server = JavaServer("mc.hypixel.net")
        >>> status = server.status()
        >>> print(f"Online: {status.online}")
        >>> print(f"Players: {status.players.online}/{status.players.max}")

        >>> # Using async
        >>> import asyncio
        >>> async def get_status():
        ...     server = JavaServer("mc.hypixel.net")
        ...     status = await server.async_status()
        ...     return status
        >>> asyncio.run(get_status())
    """

    def __init__(
        self, hostname: str, port: int = 25565, timeout: int = DEFAULT_TIMEOUT
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
    ) -> JavaServerStatusResponse | JavaServerStatusOffline:
        """
        Build response object from API data.

        Args:
            data: Raw JSON response from the API

        Returns:
            JavaServerStatusResponse if server is online, otherwise JavaServerStatusOffline
        """
        if data.get("online"):
            return JavaServerStatusResponse(
                online=data["online"],
                ip_address=data["ip_address"],
                eula_blocked=data.get("eula_blocked"),
                retrieved_at=data.get("retrieved_at"),
                expiries_at=data.get("expiries_at"),
                port=data["port"],
                version=JavaVersion(
                    name=JavaVersionName(
                        raw=data["version"].get("name_raw"),
                        clean=data["version"].get("name_clean"),
                        html=data["version"].get("name_html"),
                    ),
                    protocol=data["version"].get("protocol"),
                ),
                players=JavaPlayers(
                    max=data["players"].get("max"),
                    online=data["players"].get("online"),
                    sample=data["players"].get("sample"),
                ),
                hostname=data.get("hostname"),
                motd=MOTD(
                    raw=data["motd"]["raw"],
                    clean=data["motd"]["clean"],
                    html=data["motd"]["html"],
                ),
                icon=data.get("icon"),
                mods=data.get("mods"),
                software=data.get("software"),
                plugins=data.get("plugins"),
                srv=data.get("srv"),
            )
        else:
            return JavaServerStatusOffline(
                online=data["online"],
                hostname=data.get("hostname"),
                port=data["port"],
                ip_address=data.get("ip_address"),
                eula_blocked=data.get("eula_blocked"),
                retrieved_at=data.get("retrieved_at"),
                expiries_at=data.get("expiries_at"),
                srv=data.get("srv"),
            )

    def status(self) -> JavaServerStatusResponse | JavaServerStatusOffline:
        """
        Retrieve the server status synchronously.

        Queries the mcstatus.io API to get the current status of the Java Edition
        Minecraft server. If the hostname contains a port (e.g., "example.com:25566"),
        it will be parsed and used instead of the default port.

        Returns:
            JavaServerStatusResponse if the server is online, containing detailed
            server information including version, players, MOTD, mods, and plugins.
            JavaServerStatusOffline if the server is offline, containing basic
            information like hostname, port, and IP address.

        Raises:
            requests.exceptions.HTTPError: If the API request fails
            requests.exceptions.Timeout: If the request times out
            requests.exceptions.RequestException: For other request-related errors

        Example:
            >>> server = JavaServer("mc.hypixel.net")
            >>> status = server.status()
            >>> if status.online:
            ...     print(f"Server is online with {status.players.online} players")
            ... else:
            ...     print("Server is offline")
        """
        hostname, port = self._parse_hostname()
        url = f"{BASE_URL}/status/java/{hostname}:{port}"
        params = {"timeout": self.timeout}
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout as e:
            raise McstatusioTimeoutError("Request timed out") from e
        except requests.exceptions.ConnectionError as e:
            raise McstatusioConnectionError("Connection error occurred") from e
        except requests.exceptions.HTTPError as e:
            raise McstatusioHTTPError(
                f"HTTP error occurred: {e.response.status_code}"
            ) from e
        return self._build_response(data)

    async def async_status(self) -> JavaServerStatusResponse | JavaServerStatusOffline:
        """
        Retrieve the server status asynchronously.

        Asynchronously queries the mcstatus.io API to get the current status of the
        Java Edition Minecraft server. If the hostname contains a port (e.g.,
        "example.com:25566"), it will be parsed and used instead of the default port.

        Returns:
            JavaServerStatusResponse if the server is online, containing detailed
            server information including version, players, MOTD, mods, and plugins.
            JavaServerStatusOffline if the server is offline, containing basic
            information like hostname, port, and IP address.

        Raises:
            aiohttp.ClientError: If the API request fails
            asyncio.TimeoutError: If the request times out
            aiohttp.ClientResponseError: For HTTP error responses

        Example:
            >>> import asyncio
            >>> async def check_server():
            ...     server = JavaServer("mc.hypixel.net")
            ...     status = await server.async_status()
            ...     if status.online:
            ...         print(f"Server is online with {status.players.online} players")
            ...     else:
            ...         print("Server is offline")
            >>> asyncio.run(check_server())
        """
        hostname, port = self._parse_hostname()
        url = f"{BASE_URL}/status/java/{hostname}:{port}"
        params = {"timeout": self.timeout}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, timeout=self.timeout
                ) as response:
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
