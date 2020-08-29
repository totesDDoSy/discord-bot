"""
EventMain.py - The core discord integration logic

@author Cody Sanford <cody.b.sanford@gmail.com>
@date 2020-08-29
"""
import sqlite3
from typing import List, Union

import discord
from app.DatabaseConnector import BotDatabase


class DiscordClient(discord.Client):
    """
    The main logic of the discord bot!
    """
    def __init__(self, prefix: str):
        """
        :param prefix: Prefix to find bot commands
        """
        super().__init__()
        self.prefix = prefix
        self.db = BotDatabase()
        self.admin_commands = ['add', 'remove']
        self.static_commands = ['commands']

    @staticmethod
    async def on_disconnect():
        print('Disconnected!')

    @staticmethod
    async def on_ready():
        print('Connected to server!')

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if message.content.startswith(self.prefix):
            await self._parse_command(message)

    async def _parse_command(self, message: discord.Message):
        """
        Parse a command
        :param message: The message sent to the bot
        :return:
        """
        response_text = 'Invalid command!'
        content = message.content[len(self.prefix):]
        command = content.split(' ', 1)[0].lower()
        is_admin = self.db.is_user_admin(message.author.id)

        # List the available commands
        if command == 'commands':
            response_text = ", ".join(self._list_commands(is_admin))

        # Administration commands
        elif command in self.admin_commands and is_admin:
            cmd_type = content.split(' ', 2)[1]
            # Add/Remove Command
            if cmd_type == 'command':
                if command == 'add':
                    try:
                        self._add_text_command(content)
                        response_text = 'Command added!'
                    except sqlite3.IntegrityError as e:
                        response_text = 'A command with that name already exists!'

                elif command == 'remove':
                    self._delete_text_command(content)
                    response_text = 'Command removed!'

            # Add/Remove admin
            elif cmd_type in ['su', 'admin', 'superuser']:
                if command == 'add':
                    try:
                        self._add_admins(message.mentions)
                        response_text = 'User added as admin!'
                    except sqlite3.IntegrityError as e:
                        response_text = 'That user is already an admin!'

                elif command == 'remove':
                    if message.author.id == '170045009318510593':
                        for member in message.mentions:
                            self._delete_admin(member.id)
                    else:
                        self._delete_admin(message.author.id)
                    response_text = 'User removed from admin!'

        # Text command
        else:
            text_command = self.db.find_text_command(command, is_admin)
            if text_command:
                response_text = text_command['response']

        await message.channel.send(response_text)

    def _add_admins(self, mentions: List[discord.Member]):
        """
        Add a list of members as Admins
        Example: !add admin @user
        :param mentions: A list of members mentioned in the command
        :return:
        """
        for member in mentions:
            self.db.add_admin(member.id)

    def _delete_admin(self, user_id: Union[str, int]):
        """
        Remove a user from Admins
        Example: !remove admin
        :param user_id: Discord User ID to remove
        :return:
        """
        self.db.delete_admin(user_id)

    def _add_text_command(self, content: str):
        """
        Add a Text Command
        Example: !add command example "This is an example" <admin>
        :param content: Content of the message to parse
        :return:
        """
        admin_only = False
        _, _, command_name, response = content.split(' ', 3)
        if command_name in self.admin_commands or command_name in self.static_commands:
            return False
        if response[-5:] == 'admin':
            admin_only = True
            response = response[:-6]
        self.db.add_text_command(command_name, response.strip('"'), admin_only)

    def _delete_text_command(self, content: str):
        """
        Remove a Text Command
        Example: "!remove command example"
        :param content: Content of the message to parse
        :return:
        """
        _, _, command_name = content.split(' ', 3)
        self.db.delete_text_command(command_name)

    def _list_commands(self, is_admin=False):
        """
        List all available commands
        :param is_admin: Whether or not to display admin only commands
        :return:
        """
        command_list = []
        command_list.extend(self.static_commands)
        command_list.extend([name for _, name, _, _ in self.db.get_all_text_commands(is_admin)])
        if is_admin:
            command_list.extend(self.admin_commands)
        return command_list

