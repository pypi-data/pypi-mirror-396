from . import DataType, ModbusRegister


class DS100:
    serial_number = ModbusRegister(
        name="Serial Number",
        address=0x1000,
        count=3,
        data_type=DataType.BCD,
    )
    sw_rev = ModbusRegister(
        name="Software Revision",
        address=0x1004,
        count=1,
        data_type=DataType.UINT16,
    )
    hw_rev = ModbusRegister(
        name="Hardware Revision",
        address=0x1005,
        count=1,
        data_type=DataType.UINT16,
    )

    voltage_l1_n = ModbusRegister(
        name="Voltage L1/N",
        address=0x0400,
        count=2,
        data_type=DataType.INT32,
        scale=0.001,
        unit="V",
    )
    voltage_l2_n = ModbusRegister(
        name="Voltage L2/N",
        address=0x0402,
        count=2,
        data_type=DataType.INT32,
        scale=0.001,
        unit="V",
    )
    voltage_l3_n = ModbusRegister(
        name="Voltage L3/N",
        address=0x0404,
        count=2,
        data_type=DataType.INT32,
        scale=0.001,
        unit="V",
    )

    current_l1 = ModbusRegister(
        name="Current L1",
        address=0x0410,
        count=2,
        data_type=DataType.INT32,
        scale=0.001,
        unit="A",
    )
    current_l2 = ModbusRegister(
        name="Current L2",
        address=0x0412,
        count=2,
        data_type=DataType.INT32,
        scale=0.001,
        unit="A",
    )
    current_l3 = ModbusRegister(
        name="Current L3",
        address=0x0413,
        count=2,
        data_type=DataType.INT32,
        scale=0.001,
        unit="A",
    )

    active_power_l1 = ModbusRegister(
        name="Active Power L1",
        address=0x041A,
        count=2,
        data_type=DataType.INT32,
        unit="W",
    )
    active_power_l2 = ModbusRegister(
        name="Active Power L2",
        address=0x041C,
        count=2,
        data_type=DataType.INT32,
        unit="W",
    )
    active_power_l3 = ModbusRegister(
        name="Active Power L3",
        address=0x041E,
        count=2,
        data_type=DataType.INT32,
        unit="W",
    )
    active_power_combined = ModbusRegister(
        name="Active Power Combined",
        address=0x0420,
        count=2,
        data_type=DataType.INT32,
        unit="W",
    )

    active_energy_import = ModbusRegister(
        name="Active Energy Import",
        address=0x010E,
        count=2,
        data_type=DataType.INT32,
        scale=0.01,
        unit="kWh",
    )
    active_energy_export = ModbusRegister(
        name="Active Energy Export",
        address=0x0118,
        count=2,
        data_type=DataType.INT32,
        scale=0.01,
        unit="kWh",
    )
