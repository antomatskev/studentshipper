import os
import discord
from replit import db


class Studentshipper(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(client))

    async def on_message(self, message):
        if message.author == client.user:
            return
        else:  # Private messages.
            await self.talk_to(message)

    async def on_member_join(self, member):
        print(f"===DEBUG: {member} has joined the server!")
        await self.send_message_to(member)

    async def talk_to(self, message):
        user = message.author
        if type(message.channel) is discord.channel.DMChannel:
            print(f"===DEBUG: Message object: {message}")
            print(f"===DEBUG: Message content: {message.content}")
            print(f"===DEBUG: Message author: {user}")
            await self.send_message_to(user)

    async def send_message_to(self, user):
      try:
        state = db[user]
      except TypeError:
        state = -1
      print(f"===DEBUG: State for user {user} is {state}")
      if state == -1:
        await user.send("Hey! I'm TalTech-IT-rus server bot. I'd like to confirm you are TalTech student. Enter your university e-mail. I'll send you a confirmation code.")
      elif state == 0:
        await user.send("You again...")
      else:
        await user.send("Hello there!")


if "users" not in db.keys():
    db["users"] = {"Studentshipper": -1}

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = Studentshipper(command_prefix=".", intents=intents)
client.run(os.getenv('TOKEN'))
