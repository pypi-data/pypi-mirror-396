"""
mcstatusio - A Python wrapper for the mcstatus.io API.

This package provides simple and efficient interfaces to query Minecraft server
status information for both Java Edition and Bedrock Edition servers via the
mcstatus.io API.

Classes:
    JavaServer: Client for querying Java Edition Minecraft servers
    BedrockServer: Client for querying Bedrock Edition Minecraft servers

Example:
    >>> from mcstatusio import JavaServer
    >>> server = JavaServer("mc.hypixel.net")
    >>> status = server.status()
    >>> print(f"Players online: {status.players.online}/{status.players.max}")
"""

from .BedrockServer import BedrockServer
from .JavaServer import JavaServer

__all__ = ["BedrockServer", "JavaServer"]
__version__ = "1.0.5"
