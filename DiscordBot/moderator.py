from enum import Enum, auto
import discord
import re

class State(Enum):
    REPORT_RECEIVED = auto()
    AWAITING_CONFIDENCE = auto()
    FLAGGED = auto()
    UNSURE = auto()
    AWAITING_SOURCE = auto()
    AWAITING_MISINFO = auto()
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

            self.source = message.content
            self.state = State.AWAITING_MISINFO
            return ["Is this misinformation? Please answer 'yes' or 'no'."]
            
        
        if self.state == State.AWAITING_MISINFO:

            if message.content.strip().lower() == 'yes':
            
                self.state = AWAITING_DECEPTION
                return ["Is the misinformation provided deceptive in nature?"]
                
            elif message.content.strip().lower() == 'no':
                
                self.state = AWAITING_ABUSE
                reply = "Does this seem to be an abuse of the report system or failure in the automated detection system? "
                reply += "Please select one of the options below:\n" + 
                    "```" +
                    "1. No\n" +
                    "2. Yes, abuse\n" +
                    "3. Yes, system failure\n" +
                    "```”
                return [reply]

            else:
                return ["Please answer 'yes' or 'no'."]

        if self.state == State.AWAITING_ABUSE:
            try:
                user_choice = int(message.content)
            except ValueError:
                return []

            abuse = {
                1: "No",
                2: "Yes, abuse",
                3: "Yes, system failure"
            }

            if user_choice == 1:
                self.state = State.MODERATION_COMPLETE
                return ["No action necessary. Moderation flow complete."]
            elif user_choice == 2:
                self.state = State.MODERATION_COMPLETE
                return ["The reporting user has been banned from making further reports for 24 hours. Moderation flow complete."]
            elif user_choice = 3:
                self.state = State.FLAGGED
                return ["This report has been sent to the automated detection system development team for review."]
            else:
                return ["Please select a valid number from 1 to 3."]

        if self.state == State.AWAITING_DECEPTION:
        
            if message.content.strip().lower() == 'yes':
               
                self.state = State.AWAITING_ACTION
                reply = "Please consider the potential harm caused by the deception, our high risk subjects defined in our Trust & Safety policies, and history of the user to choose an appropriate action from below: " + 
                    "```" +
                    "1. Delete message\n" +
                    "2. Send warning\n" +
                    "3. Disable account\n" +
                    "```”
                return [reply]

            elif message.content.strip().lower() == 'no':
                self.state = State.AWAITING_CONTEXT
                
                return ["Given user history/context, does this user require disciplinary action? Please answer 'yes' or 'no'."]
                
            # Invalid response
            else:
                return ["Please answer 'yes' or 'no'."]

        if self.state == State.AWAITING_CONTEXT:
            if message.content.strip().lower() == 'yes':
               
                self.state = State.AWAITING_ACTION
                reply = "Please consider the potential harm caused by the deception, our high risk subjects defined in our Trust & Safety policies, and history of the user to choose an appropriate action from below: " + 
                    "```" +
                    "1. Delete message\n" +
                    "2. Send warning\n" +
                    "3. Disable account\n" +
                    "```”
                return [reply]

            elif message.content.strip().lower() == 'no':
                self.state = State.MODERATION_COMPLETE
                
                return ["No action necessary. Moderation flow complete."]
                
            # Invalid response
            else:
                return ["Please answer 'yes' or 'no'."]
            
        
        if self.state == State.AWAITING_ACTION:
            try:
                user_choice = int(message.content)
            except ValueError:
                return []

            abuse = {
                1: "Delete message",
                2: "Send warning",
                3: "Disable account"
            }

            if user_choice == 1:
                self.state = State.MODERATION_COMPLETE
                return ["The reported message has been deleted. Moderation flow complete."]
            elif user_choice == 2:
                self.state = State.MODERATION_COMPLETE
                return ["The reported message has been deleted. The user has been sent a warning and is now banned from messaging for 2 hours. Moderation flow complete."]
            elif user_choice = 3:
                self.state = State.FLAGGED
                return ["The reported message has been deleted and the reported user's account has been disabled. Moderation flow complete."]
            else:
                return ["Please select a valid number from 1 to 3."]
                
    def moderation_complete(self):
        return self.state == State.MODERATION_COMPLETE or State.FLAGGED
    