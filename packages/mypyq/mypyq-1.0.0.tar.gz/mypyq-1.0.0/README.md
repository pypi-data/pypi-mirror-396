# MyPythonQ

A functional (probably really bad) Python library for garage doors using myQ API.

## Installation

```bash
pip install mypythonq
```

## Usage

```python
import mypyq

# Create a MyPythonQ instance
api = mypyq.create(account_id="my_account_id", refresh_token="my_refresh_token")

# Use the API to control garage doors
doors = api.devices()
for door in doors:
    print(door.status())
    door.open()
```

## History

I created this library because I wanted to control my garage door using Python, and for my HomeAssistant integration; existing libraries stopped working becuase of the myQ API changes. This is a personal project and may not be suitable for production use.
