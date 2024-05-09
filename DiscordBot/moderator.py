from enum import Enum, auto
import discord
import re

class State(Enum):
    REPORT_RECEIVED = auto()
    AWAITING_CONFIDENCE = auto()
    FLAGGED = auto()
    UNSURE = auto()
    AWAITING_SOURCE = auto()
    AWAITING_DECEPTION = auto()
    AWAITING_ABUSE = auto()
    AWAITING_CONTEXT = auto()
    AWAITING_ACTION = auto()
    MODERATION_COMPLETE = auto()

class Moderator:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"

    def __init__(self, client):
        self.state = State.REPORT_RECEIVED
        self.client = client

        """
        I think all of this will come from the message we read from the mod channel? Not sure how to get that
        self.message = None
        self.report_details1 = None  #Details of the report I added
        self.report_details2 = None
        self.message_link = None #For reported msg link
        self.guild_id = None  # Storing guild ID
        self.reporter_id = None # store userid of reporter
        """
        self.source = None
    
    async def handle_message(self, message):
        '''
        This function makes up the meat of the moderation flow. 
        '''
        
        if self.state == State.REPORT_RECEIVED:
            reply = "This message has been reported as misinformation. "
            reply += "Are you confident whether or not the reported information is misinformation as defined by our Terms and Services? Please choose one of the options below:\n" + 
                    "```" +
                    "1. Confident\n" +
                    "2. Unsure\n" +
                    "3. Flag for higher review\n" +
                    "```”
            self.state = State.AWAITING_CONFIDENCE
            return [reply]
        
        if self.state == State.AWAITING_CONFIDENCE:
            try:
                user_choice = int(message.content)
            except ValueError:
                return []

            confidence = {
                1: "Confident",
                2: "Unsure",
                3: "Flag for higher review"
            }

            if user_choice == 1:
                self.state = State.AWAITING_SOURCE
                return ["Please enter a source from the list of pre-approved fact-checking sources."]
            elif user_choice == 2:
                self.state = State.UNSURE
                return ["Is the subject a high risk subject as defined in our Trust & Safety policies?"]
            elif user_choice = 3:
                self.state = State.FLAGGED
                return ["This report has been sent to a higher level of moderation for review."]
            else:
                return ["Please select a valid number from 1 to 3."]

                
        if self.state == State.UNSURE:

            # Yes case, make less error prone by using strip and lower
            if message.content.strip().lower() == 'yes':
               
                self.state = State.FLAGGED
                return ["This report has been sent to a higher level of moderation for review."]
                    
            elif message.content.strip().lower() == 'no':
                self.state = State.FLAGGED
                
                return ["This report has been sent to the Trust & Safety team for a review of our high risk categories and misinformation policies."]
                
            # Invalid response
            else:
                return ["Please answer 'yes' or 'no'."]
                
        if self.state == State.AWAITING_SOURCE:
        
            source = message.content
            
            if user_choice in (1, 2, 3, 4, 5, 6):
                
                self.report_details2 = reasons[user_choice]
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

            
            return ["Would you like to block this user so that you don't see any future messages from them? Please answer 'yes' or 'no'."]
            
        
        if self.state == State.BLOCKING_USER:
        
            # Yes case, make less error prone by using strip and lower
            if message.content.strip().lower() == 'yes':
            
                await self.client.send_message_to_group(self.guild_id, self) #forward message to mod channel
                self.state = State.REPORT_COMPLETE
                return ["User has been blocked. Report finished"]
                
            elif message.content.strip().lower() == 'no':
                
                await self.client.send_message_to_group(self.guild_id, self)
                self.state = State.REPORT_COMPLETE
                return ["User was not blocked. Report finished"]
                
            else:
                return ["Please answer 'yes' or 'no'."]
                
    def report_complete(self):
        return self.state == State.MODERATION_COMPLETE or State.FLAGGED
    