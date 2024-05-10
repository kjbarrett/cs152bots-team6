# bot.py
import discord
from discord.ext import commands
import os
import json
import logging
import re
import requests
import openai
from report import Report
from moderator import Moderator
import pdb

# Set up logging to the console
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# There should be a file called 'tokens.json' inside the same folder as this file
token_path = 'tokens.json'
if not os.path.isfile(token_path):
    raise Exception(f"{token_path} not found!")
with open(token_path) as f:
    # If you get an error here, it means your token is formatted incorrectly. Did you put it in quotes?
    tokens = json.load(f)
    discord_token = tokens['discord']
    OpenApi_token = tokens['openAPI']


class ModBot(discord.Client):
    def __init__(self): 
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='.', intents=intents)
        self.group_num = 6
        self.chat_client = openai.OpenAI(api_key = OpenApi_token)
        self.mod_channels = {} # Map from guild to the mod channel id for that guild
        self.reports = {} # Map from user IDs to the state of their report
        self.moderator = {}

    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord! It is these guilds:')
        for guild in self.guilds:
            print(f' - {guild.name}')
        print('Press Ctrl-C to quit.')

        # Parse the group number out of the bot's name
        match = re.search('[gG]roup (\d+) [bB]ot', self.user.name)
        if match:
            self.group_num = match.group(1)
        else:
            raise Exception("Group number not found in bot's name. Name format should be \"Group # Bot\".")

        # Find the mod channel in each guild that this bot should report to
        for guild in self.guilds:
            for channel in guild.text_channels:
                if channel.name == f'group-{self.group_num}-mod':
                    self.mod_channels[guild.id] = channel
        

    async def on_message(self, message):
        '''
        This function is called whenever a message is sent in a channel that the bot can see (including DMs). 
        Currently the bot is configured to only handle messages that are sent over DMs or in your group's "group-#" channel. 
        '''
        # Ignore messages from the bot 
        if message.author.id == self.user.id:
            return

        # Check if this message was sent in a server ("guild") or if it's a DM
        if message.guild:
            await self.handle_channel_message(message)

        else:
            await self.handle_dm(message)

    async def handle_dm(self, message):
        # Handle a help message
        if message.content == Report.HELP_KEYWORD:
            reply =  "Use the `report` command to begin the reporting process.\n"
            reply += "Use the `cancel` command to cancel the report process.\n"
            await message.channel.send(reply)
            return

        author_id = message.author.id
        responses = []

        # Only respond to messages if they're part of a reporting flow
        if author_id not in self.reports and not message.content.startswith(Report.START_KEYWORD):
            return

        # If we don't currently have an active report for this user, add one
        if author_id not in self.reports:
            self.reports[author_id] = Report(self)

        # Let the report class handle this message; forward all the messages it returns to uss
        responses = await self.reports[author_id].handle_message(message)
        for r in responses:
            await message.channel.send(r)

        # If the report is complete or cancelled, remove it from our map
        if self.reports[author_id].report_complete():
            self.reports.pop(author_id)

    async def handle_channel_message(self, message):
        # Only handle messages sent in the "group-#" channel and the mod channel
        if not (message.channel.name == f'group-{self.group_num}' or message.channel.name == f'group-{self.group_num}-mod'):
            return


#        # Forward the message to the mod channel
        mod_channel = self.mod_channels[message.guild.id]
#        
        author_id = message.author.id
        responses = []
        
#        if author_id not in self.moderator:
#            self.moderator[author_id] = Moderator(self)
            
        responses = await self.moderator[0].handle_message_1(message)
        for r in responses:
            await mod_channel.send(r)
            
#        if self.moderator[author_id].moderation_complete():
#            self.moderator.pop(author_id)
            
#        await mod_channel.send(f'Forwarded message:\n{message.author.name}: "{message.content}"')
#        scores = self.eval_text(message.content)
#        await mod_channel.send(self.code_format(scores))



    
    def eval_text(self, message):
        ''''
        TODO: Once you know how you want to evaluate messages in your channel, 
        insert your code here! This will primarily be used in Milestone 3. 
        '''
        """
        response = self.chat_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are tasked with determining if the current message is disinformation. Classify it as Yes or No."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
        """ 

        return message
      
    
    def code_format(self, text):
        ''''
        TODO: Once you know how you want to show that a message has been 
        evaluated, insert your code here for formatting the string to be 
        shown in the mod channel. 
        '''
        return "Evaluated: '" + text+ "'"

#    async def send_message_to_group(self, report):
#        # Need to fix this function
#        report_content = f'Reported Message: {report}'
#        # print(self.mod_channels)
#        # mod_channel = self.mod_channels[guild.id]
#        # await mod_channel.send(report_content)
#        mod_channel = self.mod_channels[report.guild.id]
#        await mod_channel.send(f'A user just reported a message:\n{report.author.name}: "{report.content}"')

    async def send_message_to_group(self, guild_id, report):
        
        report_content = f'Report sent by {report.reporter_id}\n'
        report_content += f'Reported Message: {report.message_link}\n'
        report_content += f'Reason for report: {report.report_details1} about {report.report_details2}'
        
        mod_channel = self.mod_channels[guild_id]
        await mod_channel.send(report_content)
        self.moderator[0] = Moderator(self)
        responses = await self.moderator[0].handle_message_1(report)
        for r in responses:
            await mod_channel.send(r)
##        for r in responses:
##            await mod_channel.send(r)
#
#
#        author_id = message.author.id
#        responses = []
#        
#        if author_id not in self.moderator:
#            self.moderator[author_id] = Moderator(self)
#            
#        responses = await self.moderator[author_id].handle_message_1(report)
#        for r in responses:
#            await mod_channel.send(r)
#            
#        if self.moderator[author_id].moderation_complete():
#            self.moderator.pop(author_id)

client = ModBot()
client.run(discord_token)
