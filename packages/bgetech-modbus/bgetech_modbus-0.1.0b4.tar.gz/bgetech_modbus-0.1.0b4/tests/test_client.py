# pytest + pytest-asyncio Version
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bgetech_modbus.client import BGEtechClient
from bgetech_modbus.exceptions import CannotConnect


class DummyRegister:
    def __init__(self, address, count=1, data_type=None, scale=1.0):
        self.address = address
        self.count = count
        self.data_type = data_type
        self.scale = scale
        self.value = None
        self.last_received = None


@pytest.fixture(autouse=True)
def patch_modbus_client(monkeypatch):
    with patch(
        "bgetech_modbus.client.AsyncModbusTcpClient", autospec=True
    ) as mock_modbus:
        mock_instance = mock_modbus.return_value
        mock_instance.connected = True
        mock_instance.connect = AsyncMock()
        mock_instance.close = MagicMock()
        yield mock_instance


@pytest.fixture
def client(patch_modbus_client):
    client = BGEtechClient("127.0.0.1", 502, 1)
    client.client = patch_modbus_client
    return client


@pytest.mark.asyncio
async def test_connect_success(client):
    client.client.connected = True
    client.client.connect = AsyncMock()
    await client.connect()
    client.client.connect.assert_awaited()


@pytest.mark.asyncio
async def test_connect_fail(client):
    client.client.connected = False
    client.client.connect = AsyncMock()
    with pytest.raises(CannotConnect):
        await client.connect()


def test_close_connected(client):
    client.client.connected = True
    client.client.close = MagicMock()
    client.close()
    client.client.close.assert_called_once()


def test_close_not_connected(client):
    client.client.connected = False
    client.client.close = MagicMock()
    client.close()
    client.client.close.assert_not_called()


@pytest.mark.asyncio
async def test_read_holding_registers(client):
    client.client.connected = True
    client.client.read_holding_registers = AsyncMock(
        return_value=MagicMock(registers=[1, 2, 3])
    )
    result = await client._read_holding_registers(10, 3)
    client.client.read_holding_registers.assert_awaited_with(
        address=10, count=3, device_id=client.device_id
    )
    assert result == [1, 2, 3]


@pytest.mark.asyncio
async def test_read_holding_registers_connects_if_needed(client):
    client.client.connected = False
    client.client.connect = AsyncMock(
        side_effect=lambda: setattr(client.client, "connected", True)
    )
    client.client.read_holding_registers = AsyncMock(
        return_value=MagicMock(registers=[1])
    )
    result = await client._read_holding_registers(1, 1)
    client.client.connect.assert_awaited()
    assert result == [1]


@pytest.mark.asyncio
async def test_convert_register_float(client):
    client.client.convert_from_registers = MagicMock(return_value=2.5)
    client.client.DATATYPE = MagicMock(INT16=1)
    client._get_datatype = MagicMock(return_value=1)
    result = await client._convert_register([1, 2], data_type=None, scale=2.0)
    assert result == 5.0


@pytest.mark.asyncio
async def test_convert_register_str(client):
    client.client.convert_from_registers = MagicMock(return_value="abc")
    client.client.DATATYPE = MagicMock(INT16=1)
    client._get_datatype = MagicMock(return_value=1)
    result = await client._convert_register([1, 2], data_type=None, scale=1.0)
    assert result == "abc"


@pytest.mark.asyncio
async def test_convert_register_list(client):
    client.client.convert_from_registers = MagicMock(return_value=[3])
    client.client.DATATYPE = MagicMock(INT16=1)
    client._get_datatype = MagicMock(return_value=1)
    result = await client._convert_register([1, 2], data_type=None, scale=2.0)
    assert result == 6.0


def test_optimize_reg_list(client):
    regs = [DummyRegister(1), DummyRegister(2), DummyRegister(20)]
    groups = client._optimize_reg_list(regs)
    assert isinstance(groups, list)
    assert all(isinstance(g, list) for g in groups)
    assert len(groups) >= 1


@pytest.mark.asyncio
async def test_read_data(client):
    client._read_holding_registers = AsyncMock(return_value=[1, 2, 3, 4])
    client._convert_register = AsyncMock(side_effect=[10, 20])
    regs = [DummyRegister(1, count=2), DummyRegister(3, count=2)]
    for r in regs:
        r.data_type = None
        r.scale = 1.0
    out = await client.read_data(regs)
    assert len(out) == 2
    assert out[0].value == 10
    assert out[1].value == 20
