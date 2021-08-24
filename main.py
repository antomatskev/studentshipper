import os
import discord
import random
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
        else:  # Private messages.
            await self.talk_to(None, message)

    async def on_member_join(self, member):
        print(f"===DEBUG: {member} has joined the server!")
        await self.talk_to(member, None)

    async def talk_to(self, member, message):
        if member:
            user = member
        else:
            user = message.author
        if type(message.channel) is discord.channel.DMChannel:
            print(f"===DEBUG: Message object: {message}")
            print(f"===DEBUG: Message content: {message.content}")
            print(f"===DEBUG: Message author: {user}")
            state = self.determine_state(user)
            answer = "Oops. Something went wrong..."
            if state == -1:  # Brand new user.
                db[user]["state"] = 0
                answer = """Hey! I'm TalTech-IT-rus server bot. I'd like to confirm you are TalTech student.

                         Enter your university e-mail. I'll send you a confirmation code."""
            elif state == 0:  # Getting e-mail and sending a code.
                if self.is_correct_mail(message):
                    state = 1
                    code = self.generate_code()
                    self.update_user(user, state, message, code)
                    answer = f"""Sending confirmation code to {message}.

                    Answer me with the code I've sent you to gain access to our discord server."""
                    self.send_code_to_mail(message, code)
                else:
                    answer = f"You entered {message}, which doesn't look like correct TalTech e-mail. Try again."
            elif state == 1:  # Wait for entering a confirmation code.
                generated_code = db[user]["code"]
                if message == generated_code:
                    self.assign_role(user)
                    self.update_user_state(user, 2)
                    answer = "Welcome to TalTech-IT-rus!"
            await self.send_message_to(user, answer)

    async def send_message_to(self, user, answer):
        await user.send(answer)

    ####### Helper methods
    def determine_state(self, user):
        ret = -1
        try:
            state = db[user]["state"]
        except TypeError:
            state = -1
        print(f"===DEBUG: State for user {user} is {state}")
        return ret

    def is_correct_mail(self, mail):
        """Check if entered e-mail's domain is correct."""
        print(f"===DEBUG: checking if an email {mail} is correct")
        return mail.endswith("ttu.ee") or mail.endswith("taltech.ee")

    def update_user_state(self, user, state):
        db[user]["state"] = state

    def update_user(self, user, state, email, code):
        db[user]["state"] = state
        db[user]["email"] = email
        db[user]["code"] = code

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
        alphabet = list('1234567890QWERTYUIOPASDFGHJKLZXCVBNM')
        return "".join(map(lambda x: random.choice(alphabet), (["0"] * 32)))

    async def assign_role(self, user):
        """Accepting user, changing the role etc."""
        jun = discord.utils.get(user.name().server.roles, name="джун")
        stud = discord.utils.get(user.name().server.roles, name="студент")
        intern = discord.utils.get(user.name().server.roles, name="стажёр")
        await client.add_roles(user.name(), jun)
        await client.add_roles(user.name(), stud)
        await client.remove_roles(user.name(), intern)


if "users" not in db.keys():
    db["users"] = {"Studentshipper": {"state": -1, "mail": "email", "code": "12345abcdef"}}

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = Studentshipper(command_prefix=".", intents=intents)
client.run(os.getenv('TOKEN'))
