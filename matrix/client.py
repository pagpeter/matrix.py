from .API import Bot

class Client:
    def __init__(self):
        """Initialize client."""
        self.loop = None
        self.client = Bot
    
    def run(self, username: str, password: str, homeserver: str, device_id: str = "") -> None:
        """
        Run client.
        :param username: username of the user
        :param password: password of the user
        :param homeserver: homeserver of the user
        """
        self.client = Bot(username, password, homeserver)
        self.client.login(device_id=device_id)
        self.client.start_sync()
        self.on_ready()
