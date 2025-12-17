from dataclasses import dataclass
from enum import Enum


class DataType(Enum):
    INT16 = "INT16"
    UINT16 = "UINT16"
    INT32 = "INT32"
    UINT32 = "UINT32"
    FLOAT32 = "FLOAT32"
    FLOAT64 = "FLOAT64"
    BCD = "BCD"


@dataclass
class ModbusRegister:
    name: str
    address: int
    count: int
    data_type: DataType
    # optional
    scale: float = 1.0
    unit: str | None = None
    # filled by client after data receive
    value: str | int | float | None = None
    last_received: int | None = None
