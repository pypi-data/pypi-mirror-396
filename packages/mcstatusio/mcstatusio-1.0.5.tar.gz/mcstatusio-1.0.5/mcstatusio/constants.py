"""
Constants and typed data models for the mcstatusio package.

This module defines all dataclass models used to represent Minecraft server status
information for both Java Edition and Bedrock Edition servers. It also provides
configuration constants like the base API URL and default timeout values.

Constants:
    BASE_URL: The base URL for the mcstatus.io API (v2)
    DEFAULT_TIMEOUT: Default request timeout in seconds (5)
"""

from dataclasses import dataclass

BASE_URL = "https://api.mcstatus.io/v2"

DEFAULT_TIMEOUT = 5  # Timeout in seconds

# Generic Constants


@dataclass(frozen=True)
class Player:
    """
    Represents a player connected to the server.

    Attributes:
        raw: Raw player name with formatting codes
        clean: Clean player name without formatting
        html: HTML-formatted player name
    """

    raw: str
    clean: str
    html: str


@dataclass(frozen=True)
class MOTD:
    """
    Message of the Day (MOTD) shown in the server list.

    The MOTD is provided in three formats for different use cases.

    Attributes:
        raw: Raw MOTD with formatting codes
        clean: Plain text MOTD without formatting
        html: HTML-formatted MOTD for web display
    """

    raw: str
    clean: str
    html: str


@dataclass(frozen=True)
class StatusResponse:
    """
    Base response data for any Minecraft server status query.

    This is the parent class for both online and offline server responses,
    containing common fields that are always present.

    Attributes:
        online: Whether the server is currently online
        port: Server port number
        ip_address: Server IP address (if resolved)
        eula_blocked: Whether the server is blocked due to EULA violations
        retrieved_at: Unix timestamp when the status was retrieved
        expiries_at: Unix timestamp when the cached status expires
    """

    online: bool
    port: int
    ip_address: str | None
    eula_blocked: bool | None
    retrieved_at: int | None
    expiries_at: int | None


# Java Constants


@dataclass(frozen=True)
class JavaVersionName:
    """
    Java Edition server version name in multiple formats.

    Attributes:
        raw: Raw version string with formatting codes
        clean: Clean version string without formatting
        html: HTML-formatted version string
    """

    raw: str
    clean: str
    html: str


@dataclass(frozen=True)
class JavaMods:
    """
    Information about a mod installed on a Java Edition server.

    Attributes:
        name: Mod name
        version: Mod version string
    """

    name: str
    version: str


@dataclass(frozen=True)
class JavaPlugins:
    """
    Information about a plugin installed on a Java Edition server.

    Attributes:
        name: Plugin name
        version: Plugin version string
    """

    name: str
    version: str


@dataclass(frozen=True)
class JavaVersion:
    """
    Java Edition server version information.

    Attributes:
        name: Version name in multiple formats
        protocol: Minecraft protocol version number
    """

    name: JavaVersionName
    protocol: int


@dataclass(frozen=True)
class JavaPlayers:
    """
    Java Edition server player information.

    Attributes:
        max: Maximum number of players allowed
        online: Number of players currently online
        sample: List of sample players (if provided by server)
    """

    max: int
    online: int
    sample: list[Player] | None


@dataclass(frozen=True)
class JavaSRV:
    """
    DNS SRV record information for a Java Edition server.

    SRV records allow Minecraft servers to use custom ports while still
    being accessible via the standard domain name.

    Attributes:
        host: SRV record target host
        port: SRV record target port
    """

    host: str
    port: int


@dataclass(frozen=True)
class JavaServerStatusOffline:
    """
    Status information for an offline Java Edition server.

    Contains basic information that can be retrieved even when the server
    is not responding.

    Attributes:
        online: Always False for offline servers
        hostname: Server hostname
        port: Server port
        ip_address: Server IP address (if resolvable)
        eula_blocked: Whether the server is EULA blocked
        retrieved_at: Unix timestamp of retrieval
        expiries_at: Unix timestamp of cache expiry
        srv: SRV record information (if available)
    """

    online: bool
    hostname: str
    port: int
    ip_address: str | None
    eula_blocked: bool
    retrieved_at: int
    expiries_at: int
    srv: JavaSRV | None


# Bedrock Constants


@dataclass(frozen=True)
class BedrockVersion:
    """
    Bedrock Edition server version information.

    Attributes:
        name: Version name string (e.g., "1.20.1")
        protocol: Minecraft protocol version number
    """

    name: str | None
    protocol: int | None


@dataclass(frozen=True)
class BedrockPlayers:
    """
    Bedrock Edition server player information.

    Attributes:
        max: Maximum number of players allowed
        online: Number of players currently online
    """

    max: int | None
    online: int | None


@dataclass(frozen=True)
class BedrockServerStatusOffline:
    """
    Status information for an offline Bedrock Edition server.

    Contains basic information that can be retrieved even when the server
    is not responding.

    Attributes:
        online: Always False for offline servers
        port: Server port
        ip_address: Server IP address (if resolvable)
        eula_blocked: Whether the server is EULA blocked
        retrieved_at: Unix timestamp of retrieval
        expiries_at: Unix timestamp of cache expiry
    """

    online: bool
    port: int
    ip_address: str | None
    eula_blocked: bool
    retrieved_at: int
    expiries_at: int


# All
__all__ = [
    "BASE_URL",
    "DEFAULT_TIMEOUT",
    "Player",
    "MOTD",
    "StatusResponse",
    "JavaVersionName",
    "JavaMods",
    "JavaPlugins",
    "JavaVersion",
    "JavaPlayers",
    "JavaSRV",
    "JavaServerStatusOffline",
    "BedrockVersion",
    "BedrockPlayers",
    "BedrockServerStatusOffline",
]
