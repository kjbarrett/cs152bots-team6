from enum import Enum, auto
import discord
import re

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    AWAITING_DETAILS = auto()  # New state I added
    REPORT_COMPLETE = auto()

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"

    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.message = None
        self.report_details1 = None  #Details of the report I added
        self.report_details2 = None
        self.message_link = None #For reported msg link
        self.guild_id = None  # Storing guild ID
    
    async def handle_message(self, message):
        '''
        This function makes up the meat of the user-side reporting flow. It defines how we transition between states and what 
        prompts to offer at each of those states. You're welcome to change anything you want; this skeleton is just here to
        get you started and give you a model for working with Discord. 
        '''

        if message.content == self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]
        
        if self.state == State.REPORT_START:
            reply =  "Thank you for starting the reporting process. "
            reply += "Say `help` at any time for more information.\n\n"
            reply += "Please copy paste the link to the message you want to report.\n"
            reply += "You can obtain this link by right-clicking the message and clicking `Copy Message Link`."
            self.state = State.AWAITING_MESSAGE
            return [reply]
        
        if self.state == State.AWAITING_MESSAGE:
            # Parse out the three ID strings from the message link
            m = re.search('/(\d+)/(\d+)/(\d+)', message.content)
            if not m:
                return ["I'm sorry, I couldn't read that link. Please try again or say `cancel` to cancel."]
            
            self.message_link = message.content  # Store the message link
            self.guild_id = int(m.group(1))
            guild = self.client.get_guild(int(m.group(1)))

            if not guild:
                return ["I cannot accept reports of messages from guilds that I'm not in. Please have the guild owner add me to the guild and try again."]
            channel = guild.get_channel(int(m.group(2)))
            if not channel:
                return ["It seems this channel was deleted or never existed. Please try again or say `cancel` to cancel."]
            try:
                message = await channel.fetch_message(int(m.group(3)))
            except discord.errors.NotFound:
                return ["It seems this message was deleted or never existed. Please try again or say `cancel` to cancel."]

            # Here we've found the message - it's up to you to decide what to do next!
            self.state = State.MESSAGE_IDENTIFIED
#            return ["I found this message:", "```" + message.author.name + ": " + message.content + "```", \
#                    "This is all I know how to do right now - it's up to you to build out the rest of my reporting flow!"]

            # new code to handle our report flow
            return ["I found this message:", "```" + message.author.name + ": " + message.content + "```", \
                    "Please select a reason for reporting this message using the numbers 1 through 4: \n 1. Harmful misinformation \n 2. Abuse or harassment \n 3. Spam \n 4. Other"]
                    

            
        
        if self.state == State.MESSAGE_IDENTIFIED:
            
            #Currently only handles when user selects harmful misinformation
            user_choice = int(message.content)
            
            if user_choice == 1:
                self.report_details1 = "Harmful misinformation"
                self.state = State.AWAITING_DETAILS
                return ["What kind of harmful misinformation? \n 1. Election \n 2. Placeholder1 \n 3. Placeholder2 \n 4. Other"]
        
                    
            # return ["<insert rest of reporting flow here>"]
        
        #new state handler
        if self.state == State.AWAITING_DETAILS:
        
            #currently only handles Election choice
            detail_choice = int(message.content)
            if detail_choice == 1:
                self.report_details2 = "The Election"
                await self.client.forward_report(self.guild_id, self)
                self.state = State.REPORT_COMPLETE
                return ["Thank you for reporting this message. It has been forwarded to the moderation team."]
            

        return []

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE
        

    


    

