# Zelepy
![PyPI](https://img.shields.io/pypi/v/zelepy)
![License](https://img.shields.io/github/license/mrcoolguy640/zelepy)

Zelepy is a Python wrapper for the [Zelesis Neo API](https://zelesis.com/), allowing you to communicate with the Zelesis Neo software from Python.

## Installation
```bash
pip install zelepy
```

## Features
- **Event Listening**: Listen for Neo events over UDP (detections, triggerbot, etc.)
- **Command Broadcasting**: Send commands to control Zelesis Neo (mouse movement, clicks, detection requests)
- **Configuration Management**: Read and write Zelesis Neo configuration files
- **Helper Utilities**: Get installation paths, versions, and image compression utilities

## Quickstart
### Zelesis Client
The Zelesis Client is used to broadcast or listen for events via UDP. It can be initialized via:
```py
from zelepy.events import ZelesisClient
client = ZelesisClient()
client.start()
```
Remember when you are finished with the client to run
```py
client.stop()
```
Or, you can simply use the client like a context manager, which will not require you to stpo the client once you are finished with it:
```py
from zelepy.events import ZelesisClient
with ZelesisClient() as client:
    print(f"Client is running: {client.is_running}")
```
When initializing you can set options:
```python
from zelepy.events import ZelesisClient

client = ZelesisClient(
    receive_port: int = 26512,      # Port to listen for events
    send_port: int = 26513,         # Port to send commands
    target_ip: str = "127.0.0.1",   # IP address of Zelesis Neo
    timeout: float = 2.0            # Command response timeout (seconds)
)
```

### Event Listening
```python
from zelepy.events import ZelesisClient

def on_detection(event):
    print(f"Detection: {event}")

def on_triggerbot(event):
    print(f"Triggerbot: {event}")

def on_any_event(event):
    print(f"Recieved an event: {event}")

with ZelesisClient() as client:
    # You can subscribe to specific events
    client.subscribe("detection", on_detection)
    client.subscribe("triggerbot", on_triggerbot)

    # Or you can create a generic listener that will be called whenever ANY event is received
    client.add_event_listener(on_any_event)

    # You must start the client to be able to listen to events
    client.start()

    # Client runs until context exits
```

### Event Broadcasting
#### Mouse Functions
```py
from zelepy.events import ZelesisClient

with ZelesisClient() as client:
    # No need to run client.start() here as its being used as a context manager
    # Move mouse by x, y pixels. Note that this is relative to its current position, rather than moving to an absolute position on screen
    client.move_mouse(100, 50)
    # Left click the mouse
    client.click_mouse()
```