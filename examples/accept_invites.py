import matrix 

class MyClient(matrix.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message: matrix.Message):
        pass 

    async def on_invite(self, invite: matrix.Invite):
        await invite.accept()
        self.client.send_message(invite.room_id, "Hello!")

client = MyClient()
client.run(
    username='@bot:matrix.org',
    password='password',
    homeserver='https://matrix.org',
)