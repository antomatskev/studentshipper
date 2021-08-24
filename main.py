import os
import random

import discord
import yagmail
from keep_alive import keep_alive
from replit import db


class Studentshipper(discord.Client):
    """The class representing the discord bot, extends discord.py's Client class."""

    def __init__(self, *args, **kwargs):
        """Constructor with the server field."""
        super().__init__(*args, **kwargs)
        self._server = None

    async def on_ready(self):
        """This method is invoked after the bot is loaded and ready to use."""
        print('We have logged in as {0.user}'.format(client))
        self._server = client.get_guild(int(os.getenv('SERVER_ID')))

    async def on_message(self, message):
        """When the bot sees a new message, this method is invoked."""
        if message.author == client.user:
            return
        # Private messages.
        await self.talk_to(message)

    async def on_member_join(self, member):
        """When somebody joins the server, this method is invoked."""
        print(f"===DEBUG: {member} has joined the server!")
        await self.talk_to_newbie(member)

    async def talk_to_newbie(self, user):
        """This method is invoked, when somebody joins the server, the bot counts such user as newbie and starts
        a conversation."""
        print(f"===DEBUG: talking to newbie {user}")
        if user:
            self.add_user(user)
            self.update_user_state(user, 0)
            answer = """Hey! I'm TalTech-IT-rus server bot. I'd like to confirm you are TalTech student. Enter your university e-mail. I'll send you a confirmation code."""
            await self.send_message_to(user, answer)

    async def talk_to(self, message):
        """This is method for talking to users. A talk depends on user's state:
            -1 - newbie;
            0  - saved user;
            1  - user with correct e-mail;
            2  - confirmed user;
        """
        msg = message.content
        user = message.author
        if type(message.channel) is discord.channel.DMChannel:
            # print(f"===DEBUG: Message object: {message}")
            print(f"===DEBUG: Message content: {msg}, message author: {user}")
            state = self.determine_state(user)
            answer = "Oops. Something went wrong... Please contact the server's administrator."
            if state == -1:  # Brand new user.
                await self.talk_to_newbie(user)
                return
            elif state == 0:  # Getting e-mail and sending a code.
                if self.is_correct_mail(msg):
                    state = 1
                    code = self.generate_code()
                    self.update_user(user, state, msg, code)
                    answer = f"""Sending confirmation code to {msg}. Answer me with the code I've sent you to gain access to our discord server. My letter could be in 'Junk Email'."""
                    self.send_code_to_mail(msg, code)
                else:
                    answer = f"You entered '{msg}', which doesn't look like correct TalTech e-mail. Try again."
            elif state == 1:  # Wait for entering a confirmation code.
                generated_code = db["users"][self.get_username(user)]["code"]
                print(f"===DEBUG: comparing generated code and entered code {msg}")
                if msg == generated_code:
                    await self.assign_role(message)
                    self.update_user_state(user, 2)
                    answer = "Welcome to TalTech-IT-rus!"
            await self.send_message_to(user, answer)

    ####### Helper methods
    async def send_message_to(self, user, answer):
        """Helper for sending messages."""
        print(f"===DEBUG: sending to {user} the following message: {answer}")
        await user.send(answer)

    def determine_state(self, user):
        """Helper for determining user's state, which is saved to the db."""
        try:
            ret = db["users"][self.get_username(user)]["state"]
        except TypeError:
            ret = -1
        except KeyError:
            ret = -1
        print(f"===DEBUG: State for user {user} is {ret}")
        return ret

    def is_correct_mail(self, mail):
        """Check if entered e-mail's domain is correct."""
        print(f"===DEBUG: checking if an email {mail} is correct")
        return mail.endswith("ttu.ee") or mail.endswith("taltech.ee")

    def add_user(self, user):
        """Adds a user to the db."""
        print(f"===DEBUG: adding {user} to the database")
        db["users"][self.get_username(user)] = {"state": -1, "email": "email", "code": "12345abcdef"}

    def update_user_state(self, user, state):
        """Updates user's state in the db."""
        print(f"===DEBUG: updating {user}'s state to {state}")
        username = self.get_username(user)
        db["users"][username]["state"] = state
        # print(f"===DEBUG: updated to {db['users'][username]}")

    def update_user(self, user, state, email, code):
        """Updates user's state, e-mail and code in the db."""
        # print(f"===DEBUG: updating {user} with state {state}, email {email}, code {code}")
        username = self.get_username(user)
        db["users"][username]["state"] = state
        db["users"][username]["email"] = email
        db["users"][username]["code"] = code
        # print(f"===DEBUG: updated to {db['users'][username]}")

    def send_code_to_mail(self, email, code):
        """Send an e-mail with the code."""
        body = f"""Hey!
                Here is your discord server's code:

                    {code}

                Tell it to the Studentshipper discord bot."""
        usr = os.getenv('MAIL')
        pas = os.getenv('PASS')
        if usr and pas:
            yag = yagmail.SMTP(usr, pas)
            yag.send(to=email, subject="Studentshipper confirmation code", contents=body)
        else:
            print(f"===DEBUG: sending code to {email} failed.")

    def generate_code(self):
        """Generate verification code."""
        print(f"===DEBUG: generating code...")
        alphabet = list('1234567890QWERTYUIOPASDFGHJKLZXCVBNM')
        return "".join(map(lambda x: random.choice(alphabet), (["0"] * 32)))

    async def assign_role(self, message):
        """Accepting user, changing the role etc."""
        user = self._server.get_member(message.author.id)
        print(f"===DEBUG: assigning roles to {user}, {type(user)}")
        jun = discord.utils.get(self._server.roles, name="джун")
        stud = discord.utils.get(self._server.roles, name="студент")
        intern = discord.utils.get(self._server.roles, name="стажёр")
        await user.add_roles(jun)
        await user.add_roles(stud)
        await user.remove_roles(intern)

    def get_username(self, user):
        """Helper for getting a username consisting of name and discriminator."""
        return user.name + '#' + user.discriminator


# Initiate db with the bot itself.
if "users" not in db.keys():
    db["users"] = {"Studentshipper": {"state": -1, "email": "email", "code": "12345abcdef"}}

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = Studentshipper(command_prefix=".", intents=intents)
keep_alive()
client.run(os.getenv('TOKEN'))
