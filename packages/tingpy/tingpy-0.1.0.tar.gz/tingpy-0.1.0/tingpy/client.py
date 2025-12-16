import time
from firebase_admin import credentials, initialize_app, messaging


class TingClient:
    def __init__(self, config_path):
        self.creds = credentials.Certificate(config_path)
        self.firebase_app = initialize_app(self.creds)

    def send(self, topic, title, body, color=None):
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={
                'timestamp': str(time.time()),
                'color': color or '',
            },
            topic=topic,
        )
        try:
            messaging.send(message, app=self.firebase_app)
        except Exception as e:
            print(f"Error sending notification: {e}")
