# tingpy

A developer-friendly wrapper for Firebase Cloud Messaging (FCM) that simplifies push notifications and handles mobile app pairing via QR code.

## Features

- **Notification Sender**: Send push notifications to mobile apps using Firebase Cloud Messaging.
- **Mobile Pairing**: Generate QR codes in the terminal for easy connection of mobile apps to Firebase projects.

## Installation

```bash
pip install tingpy
```

## Dependencies

- firebase-admin
- segno

## Usage

```python
import tingpy

# 1. Setup (Sending)
bot = tingpy.Client("my-secret.json")

# 2. Pairing (Only needed once)
# This prints a giant QR code in the terminal
tingpy.pair_device("google-services.json")

# 3. Usage
bot.send(
    topic="general",
    title="Trade Executed",
    body="Bought NIFTY 21500 CE @ 120"
)
```

## API Reference

### TingClient

- `__init__(config_path)`: Initialize with path to Firebase service account JSON.
- `send(topic, title, body, color=None)`: Send a notification to the specified topic.

### pair_device(json_path)

Parses the google-services.json file and prints a QR code containing the necessary pairing information.

## Testing

Run unit tests:

```bash
python -m unittest tests/test_pairing.py
```

## License

MIT
