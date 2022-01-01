import matrix 

class MyClient(matrix.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message: matrix.Message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        print(f"{message.room.id} || {message.author}: {message.content}")

        if message.content == 'ping':
            await message.reply('pong')

    async def on_invite(self, invite: matrix.Invite):
        print(f"{invite.inviter} has invited you to join {invite.room_id}")
        await invite.accept()

client = MyClient()
client.run(
    username='@bot:matrix.org',
    password='password',
    homeserver='https://matrix.org',
)