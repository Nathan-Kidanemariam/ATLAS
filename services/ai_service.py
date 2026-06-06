import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class AIService:
    """
    Handles the AI responses for ATLAS using Groq AI

    This AI service connects on Groq
    sends user prompts, and returns short responses

    FEATURES:
        1. Groq AI connection
        2. Personality
        3. Memory
        4. Conversation history
    """
    def __init__(self):
        """
        Sets up the AI service

        Creates the Groq client and starts an empty
        conversation history
        """

        #Loads API key from .env
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        #Stores recent messages for short term memory
        self.history = []

    def ask(self, user_text, context=None):
        """
        Sends a prompt to the AI model

        Gives the AI personality, user memory,
        and recent conversation history before asking the model

        ARGS:
            user_text (str): User command or question
            context (str): Optional saved memory about the user

    RETURNS:
        str: AI response text
        """

        #ATLAS personality with saved user context if possible
        try:

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are ATLAS, a futuristic AI assistant "
                        "with a witty personality, calm confidence, and high intelligence. "
                        "Keep responses conversational, short, and natural."
                    )
                }
            ]

            if context:
                messages.append({
                    "role": "system",
                    "content": (
                        f"Useful memory/context about the user:\n{context}"
                    )
                })

            # short-term conversation memory
            messages.extend(self.history)

            # current user message
            messages.append({
                "role": "user",
                "content": user_text
            })

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.6,
                max_tokens=120
            )

            answer = response.choices[0].message.content

            # store conversation memory
            self.history.append({
                "role": "user",
                "content": user_text
            })

            self.history.append({
                "role": "assistant",
                "content": answer
            })

            # keep recent memory only
            self.history = self.history[-10:]

            return answer

        except Exception as e:
            return "I am having trouble connecting to my intelligence systems."