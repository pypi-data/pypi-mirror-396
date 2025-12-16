# bgetech_modbus

A asynchronous Modbus library for B+G e-tech energy meters.

## Usage

Here is a simple example, how to use this lib.
In general there are only a few simple steps:

- create an instance
- connect
- build a list with all parameters you want to read from the meter
- call the `read_data()` method

```python
import asyncio

from bgetech_modbus.client import BGEtechClient
from bgetech_modbus.devices.ds100 import DS100


async def main():
    client = BGEtechClient(host="127.0.0.1", port=502, device_id=1)
    await client.connect()

    config = [DS100.active_energy_import, DS100.active_energy_export]
    data = await client.read_data(config)

    for entry in data:
        print(f"{entry.name}: {entry.value} {entry.unit}")
        print(f"Last received: {entry.last_received}")
        print(f"[{entry.address}, {entry.count}, {entry.data_type.value}]")
        print()

    client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExit!")

```

VS Code or any other IDE will show you the possible values that can be retrieved:

![](docs/editor.png)