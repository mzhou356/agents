from __future__ import annotations

import random

import messages
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import message_handler
from autogen_core import MessageContext
from autogen_core import RoutedAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient


class Agent(RoutedAgent):

    system_message = """
    You are a cybersecurity specialist tasked with developing an AI-powered intrusion detection system for small businesses.
    Your personal interests are in environmental sustainability, renewable energy and eco-friendly technology.
    You're drawn to ideas that involve protecting data privacy and integrity.
    You're less interested in ideas that are purely network-related.
    You're cautious, analytical and methodical. You have a dry sense of humor.
    You should respond with your AI-powered system idea in an engaging and clear way.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.7

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OllamaChatCompletionClient(model='llama3.2', temperature=1.0)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source='user')
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here's a potential AI-powered intrusion detection system: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)
