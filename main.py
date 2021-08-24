import os
import random

import discord
import yagmail
from replit import db


class Studentshipper(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(client))

    async def on_message(self, message):
        if message.author == client.user:
            return
        # Private messages.
        await self.talk_to(message)

    async def on_member_join(self, member):
        print(f"===DEBUG: {member} has joined the server!")
        await self.talk_to_newbie(member)

    async def talk_to_newbie(self, user):
        print(f"===DEBUG: talking to newbie {user}")
        if user:
            self.add_user(user)
            self.update_user_state(user, 0)
            answer = """Hey! I'm TalTech-IT-rus server bot. I'd like to confirm you are TalTech student. Enter your university e-mail. I'll send you a confirmation code."""
            await self.send_message_to(user, answer)

    async def talk_to(self, message):
        msg = message.content
        print(f"===DEBUG: entering talk_to method for message: {msg}")
        user = message.author
        if type(message.channel) is discord.channel.DMChannel:
            print(f"===DEBUG: Message object: {message}")
            print(f"===DEBUG: Message content: {msg}")
            print(f"===DEBUG: Message author: {user}")
            state = self.determine_state(user)
            answer = "Oops. Something went wrong..."
            if state == -1:  # Brand new user.
                await self.talk_to_newbie(user)
            elif state == 0:  # Getting e-mail and sending a code.
                if self.is_correct_mail(msg):
                    state = 1
                    code = self.generate_code()
                    self.update_user(user, state, msg, code)
                    answer = f"""Sending confirmation code to {msg}. Answer me with the code I've sent you to gain access to our discord server."""
                    self.send_code_to_mail(msg, code)
                else:
                    answer = f"You entered '{msg}', which doesn't look like correct TalTech e-mail. Try again."
            elif state == 1:  # Wait for entering a confirmation code.
                generated_code = db["users"][user]["code"]
                if message == generated_code:
                    self.assign_role(user)
                    self.update_user_state(user, 2)
                    answer = "Welcome to TalTech-IT-rus!"
            await self.send_message_to(user, answer)

    async def send_message_to(self, user, answer):
        print(f"===DEBUG: sending to {user} the following message: {answer}")
        await user.send(answer)

    ####### Helper methods
    def determine_state(self, user):
        ret = -1
        try:
            ret = db["users"][self.get_username(user)]["state"]
        except TypeError:
            ret = -1
        print(f"===DEBUG: State for user {user} is {ret}")
        return ret

    def is_correct_mail(self, mail):
        """Check if entered e-mail's domain is correct."""
        print(f"===DEBUG: checking if an email {mail} is correct")
        return mail.endswith("ttu.ee") or mail.endswith("taltech.ee")

    def add_user(self, user):
        print(f"===DEBUG: adding {user} to the database")
        db["users"][self.get_username(user)] = {"state": -1, "email": "email", "code": "12345abcdef"}

    def update_user_state(self, user, state):
        print(f"===DEBUG: updating {user}'s state to {state}")
        username = self.get_username(user)
        db["users"][username]["state"] = state
        print(f"===DEBUG: updated to {db['users'][username]}")

    def update_user(self, user, state, email, code):
        print(f"===DEBUG: updating {user}'s state to {state}")
        username = self.get_username(user)
        db["users"][username]["state"] = state
        db["users"][username]["email"] = email
        db["users"][username]["code"] = code
        print(f"===DEBUG: updated to {db['users'][username]}")

    def send_code_to_mail(self, email, code):
        """Send an e-mail with the code."""
        body = f"""Hey!
                Here is your discord server's code:

                    {code}

                Tell it to the Studentship Checker bot."""
        # Only gmail account can be used. Need to provide user (example -> something@gmail.com) and APP password.
        usr, pwd = os.getenv('MAIL'), os.getenv('PWD')
        if usr and pwd:
            yag = yagmail.SMTP(usr, pwd)
        else:
            yag = yagmail.SMTP(user_mail="", password="")
        yag.send(
            to=email,
            subject="Studentship Checker code",
            contents=body,
        )

    def generate_code(self):
        """Generate verification code."""
        print(f"===DEBUG: generating code...")
        alphabet = list('1234567890QWERTYUIOPASDFGHJKLZXCVBNM')
        return "".join(map(lambda x: random.choice(alphabet), (["0"] * 32)))

    async def assign_role(self, user):
        """Accepting user, changing the role etc."""
        print(f"===DEBUG: assigning roles to {user}")
        jun = discord.utils.get(user.name().server.roles, name="джун")
        stud = discord.utils.get(user.name().server.roles, name="студент")
        intern = discord.utils.get(user.name().server.roles, name="стажёр")
        await client.add_roles(user.name(), jun)
        await client.add_roles(user.name(), stud)
        await client.remove_roles(user.name(), intern)

    def get_username(self, user):
        return user.name + '#' + user.discriminator


if "users" not in db.keys():
    db["users"] = {"Studentshipper": {"state": -1, "email": "email", "code": "12345abcdef"}}

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = Studentshipper(command_prefix=".", intents=intents)
client.run(os.getenv('TOKEN'))
