# tests/test_java.py 
from mcstatusio import JavaServer
import pytest 

@pytest.mark.asyncio
async def test_java_async_server_status():
    server = JavaServer("donutsmp.net")
    status = await server.async_status()

    assert status.players.online >= 0
    assert status.players.max > 0
    assert isinstance(status.motd.clean, str)
    assert status.online is True

def test_java_sync_server_status():
    server = JavaServer("donutsmp.net")
    status = server.status()

    assert status.players.online >= 0
    assert status.players.max > 0
    assert isinstance(status.motd.clean, str)
    assert status.online is True

