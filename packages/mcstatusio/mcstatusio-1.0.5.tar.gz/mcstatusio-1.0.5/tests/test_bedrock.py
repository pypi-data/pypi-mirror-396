# tests/test_bedrock
from mcstatusio import BedrockServer
import pytest

@pytest.mark.asyncio
async def test_bedrock_async_server_status():
    server = BedrockServer("donutsmp.net", 19132)
    status = await server.async_status()

    assert status.players.online >= 0
    assert status.players.max > 0
    assert isinstance(status.motd.clean, str)
    assert isinstance(status.version.name, str)

def test_bedrock_sync_server_status():
    server = BedrockServer("donutsmp.net", 19132)
    status = server.status()

    assert status.players.online >= 0
    assert status.players.max > 0
    assert isinstance(status.motd.clean, str)
    assert isinstance(status.version.name, str)


