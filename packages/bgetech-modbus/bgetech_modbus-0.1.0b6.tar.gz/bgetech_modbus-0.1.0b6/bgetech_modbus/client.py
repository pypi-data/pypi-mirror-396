import time
from typing import List, Union

from pymodbus.client import AsyncModbusTcpClient

from .devices import DataType, ModbusRegister
from .exceptions import CannotConnect


class BGEtechClient:
    def __init__(self, host: str, port: int = 502, device_id: int = 1):
        self.host = host
        self.port = port
        self.device_id = device_id
        self.client = AsyncModbusTcpClient(host=self.host, port=self.port)

    async def connect(self):
        await self.client.connect()
        if not self.client.connected:
            raise CannotConnect(f"Cannot connect to {self.host}:{self.port}")

    def close(self):
        if self.client and self.client.connected:
            self.client.close()

    async def _read_holding_registers(self, address: int, count: int):
        if not self.client or not self.client.connected:
            await self.connect()
        result = await self.client.read_holding_registers(
            address=address, count=count, device_id=self.device_id
        )
        return result.registers if result else None

    async def _convert_register(
        self, registers, data_type: DataType, scale: float = 1.0
    ) -> float | str:
        value = self.client.convert_from_registers(
            registers=registers, data_type=self._get_datatype(data_type)
        )
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            value = value[0]
        return value * scale

    def _get_datatype(self, data_type: DataType) -> AsyncModbusTcpClient.DATATYPE:
        if data_type == DataType.INT16:
            return self.client.DATATYPE.INT16
        elif data_type == DataType.INT32:
            return self.client.DATATYPE.INT32
        elif data_type == DataType.UINT16:
            return self.client.DATATYPE.UINT16
        elif data_type == DataType.UINT32:
            return self.client.DATATYPE.UINT32
        elif data_type == DataType.FLOAT32:
            return self.client.DATATYPE.FLOAT32
        elif data_type == DataType.FLOAT64:
            return self.client.DATATYPE.FLOAT64
        else:
            raise ValueError(f"Invalid data type: {data_type}")

    def _optimize_reg_list(
        self, register: list[ModbusRegister]
    ) -> list[list[ModbusRegister]]:
        gap_threshold = 10

        # remove duplicates (using address as key in set)
        dedup = {reg.address: reg for reg in register}

        # sort by address
        register = list(dedup.values())
        register.sort(key=lambda x: x.address)

        # grouping
        optimized_groups: List[List[ModbusRegister]] = []
        current_group: List[ModbusRegister] = []

        for reg in register:
            if not current_group or (
                reg.address
                > (
                    current_group[-1].address
                    + current_group[-1].count
                    - 1
                    + gap_threshold
                )
            ):
                # start new group
                current_group = [reg]
                optimized_groups.append(current_group)
            else:
                current_group.append(reg)

        return optimized_groups

    async def read_data(self, register: list[ModbusRegister]):
        conv: Union[str, int, float]
        output = []
        for group in self._optimize_reg_list(register):
            start_address = group[0].address
            read_length = group[-1].address + group[-1].count - start_address
            raw_data = await self._read_holding_registers(start_address, read_length)

            for reg in group:
                slice_start = reg.address - start_address
                slice_end = slice_start + reg.count
                sliced_data = raw_data[slice_start:slice_end]

                if reg.data_type is DataType.BCD:
                    conv = ""
                    for reg_value in sliced_data:
                        hex_string = f"{reg_value:04x}"
                        conv += hex_string
                    conv = conv[: len(sliced_data) * 4]
                else:
                    conv = await self._convert_register(
                        sliced_data,
                        data_type=reg.data_type,
                        scale=reg.scale,
                    )

                reg.value = conv
                reg.last_received = int(time.time())
                output.append(reg)

        return output
