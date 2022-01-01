import matrix 

class MyClient(matrix.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message: matrix.Message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        # log messages
        print(f"{message.room.id} || {message.author}: {message.content}")

        if message.content.lower() == 'ping':
            await message.reply('Pong!')

            # or, you can use
            # await message.room.send("pong!")

    async def on_invite(self, invite: matrix.Invite):
        pass

client = MyClient()
client.run(
    username='@bot:matrix.org',
    password='password',
    homeserver='https://matrix.org',
)