# Discord bot for checking a studentship
A discord bot, which will check if a person is a student, then assign corresponding role to that person.

## What we want
Don't let any unwanted people post to a discord server until they confirm that they belong to a school/college/university this server is meant for. We assume, that such institution has own e-mails, so it's ensured, that a person is officially registered. In our case we are talking about TalTech.

## What we do
After a person joins a discord server, our bot does the following:

- Writes a private message to the joined person asking for an e-mail to send confirmation code;
- Sends a code to the entered e-mail and waits for a person to enter this code to the same private chat;
- If the entered code is correct, assign roles to a person and remove the initial role;

For sending e-mails we use https://github.com/kootenpv/yagmail

## Environment variables
We have several environment variables to hide things, which shouldn't be seen by anyone:

- MAIL - holds the e-mail address the bot will send mails from;
- PASS - holds the e-mail's password;
- SERVER_ID - the discord server's id, where the bot is used;
- TOKEN - the discord bot's API token;
