# ThunkMetrc

High-level Python SDK for Metrc with convenience functions like `active_packages_inventory_sync`.

## Installation

```bash
pip install thunkmetrc
```

## Usage

```python
from thunkmetrc import active_packages_inventory_sync
from thunkmetrc_wrapper import MetrcWrapper

wrapper = MetrcWrapper("https://api.metrc.com", "vendor_key", "user_key")

# Sync active packages inventory
packages = active_packages_inventory_sync(
    wrapper,
    "license_number",
    last_known_sync=None,
    buffer_minutes=5
)
```

## License

MIT
