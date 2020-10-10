import discord

f = open('../secret.txt', 'r')


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.content.startswith('$'):
            print(str(message.author) + ': ' + message.content[1:])

        if message.author == client.user:
            return

        elif message.content.startswith('$help') or message.content.startswith('-info'):
            await message.channel.send('TODO')

        elif message.content.startswith('$'):
            await message.channel.send('Hello! I\'m a Discord bot <@449579826278563860> made!\nMy prefix is `$`\nFor '
                                       'a list of commands, type `$help` or `$info`')


client = MyClient()
client.run(f.readline())
f.close()
