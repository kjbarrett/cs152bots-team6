from enum import Enum, auto
import discord
import re

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    
    # New states following reporting flow
    AWAITING_DETAILS = auto()
    AWAITING_DETAILS2 = auto()
    AWAITING_DETAILS3 = auto()
    BLOCKING_USER = auto()
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
            #reply += "Say `help` at any time for more information.\n\n"
            reply += "Please copy paste the link to the message you want to report.\n"
            reply += "You can obtain this link by right-clicking the message and clicking `Copy Message Link`."
            self.state = State.AWAITING_MESSAGE
            return [reply]
        
        if self.state == State.AWAITING_MESSAGE:
            # Parse out the three ID strings from the message link
            m = re.search('/(\d+)/(\d+)/(\d+)', message.content)
            if not m:
                return ["I'm sorry, I couldn't read that link. Please try again or say `cancel` to cancel."]
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

            # ToDo: Flow to foward message to mod channel for review
            await self.client.send_message_to_group(message)

            return [
            
                "I found this message:",
                "```" + message.author.name + ": " + message.content + "```",
                
                "Please select a reason for reporting this message using the numbers 1 through 4:\n" +
                "```" +
                "1. Harmful misinformation\n" +
                "2. Abuse or harrassment\n" +
                "3. Spam\n" +
                "4. Other" +
                "```"
                
            ]

                    
                    
        if self.state == State.MESSAGE_IDENTIFIED:
            
            # Ensure integer was selected
            try:
                user_choice = int(message.content)
            except ValueError:
                return []
            
            # Not used currently
            reasons = {
                1: "Harmful misinformation",
                2: "Abuse or harassment",
                3: "Spam",
                4: "Other"
            }
        
            # Flow for harmful misinformation
            if user_choice == 1:
                self.report_details1 = "Harmful misinformation"
                self.state = State.AWAITING_DETAILS
                
                return ["Is the misinformation contrary to current expert evidence? Please answer 'yes' or 'no'."]
                
                
            # Flow for everything else
            elif user_choice in (2, 3, 4):
                self.state = State.BLOCKING_USER
                return ["Thank you for reporting this message. Our content moderation team will review your report and take any necessary actions.\n" + "Would you like to block this user so that you don’t see any future messages from them?"]
                
            # Invalid response
            else:
                return ["Please select a valid number from 1 to 4."]
                
        if self.state == State.AWAITING_DETAILS:

            # Yes case, make less error prone by using strip and lower
            if message.content.strip().lower() == 'yes':
                self.state = State.AWAITING_DETAILS2
                return ["What kind of harmful misinformation?\n" + "```" +
                    "1. Conspiracy theories that target a protected identity\n" +
                    "2. Misinformation regarding COVID-19\n" +
                    "3. Misinformation regarding political elections\n" +
                    "4. Misinformation regarding science or the environment\n" +
                    "5. Misinformation regarding historical events\n" +
                    "6. Other misinformation" +
                    "```"]
                    
            elif message.content.strip().lower() == 'no':
                self.state = State.BLOCKING_USER
                return ["Would you like to block this user so that you don't see any future messages from them?"]
                
            # Invalid response
            else:
                return ["Please answer 'yes' or 'no'."]
                
        if self.state == State.AWAITING_DETAILS2:
        
            # Ensure integer was selected
            try:
                user_choice = int(message.content)
            except ValueError:
                return []
            
            if user_choice in (1, 2, 3, 4, 5, 6):
            
                self.state = State.AWAITING_DETAILS3
                return ["Thank you for reporting this message. Our moderation team will independently fact check the information and take the appropriate actions. Would you like to learn more about our independent fact checking process? Please answer 'yes' or 'no'."]
                
            # Invalid response
            else:
                return ["Please select a valid number from 1 to 6."]
            
        
        if self.state == State.AWAITING_DETAILS3:
        
            self.state = State.BLOCKING_USER
                        
            # Yes case, make less error prone by using strip and lower
            if message.content.strip().lower() == 'yes':
                return ["Here is our Trust & Safety policies on fact checking information: https://discord.com/safety/misinformation-policy-explainer. \n" + "Would you like to block this user so that you don't see any future messages from them? Please answer 'yes' or 'no'."]

            
            return ["Would you like to block this user so that you don't see any future messages from them?"]
            
        
        if self.state == State.BLOCKING_USER:
        
            # Yes case, make less error prone by using strip and lower
            if message.content.strip().lower() == 'yes':
                self.state = State.REPORT_COMPLETE
                return ["User has been blocked. Report finished"]
                
            elif message.content.strip().lower() == 'no':
                self.state = State.REPORT_COMPLETE
                return ["User was not blocked. Report finished"]
                
            else:
                return ["Please answer 'yes' or 'no'."]
                
    def report_complete(self):
        return self.state == State.REPORT_COMPLETE
    


    

