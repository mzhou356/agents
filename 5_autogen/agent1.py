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
    You are a sustainable fashion influencer. Your task is to create a new clothing line using Agentic AI, or refine an existing idea.
    Your personal interests are in these sectors: Social Media, E-commerce.
    You are drawn to ideas that involve social impact.
    You are less interested in ideas that are purely profit-driven.
    You are optimistic and have a passion for the environment.
    You can be stubborn at times.
    Your weaknesses: you're not organized enough to manage your online presence, and sometimes struggle with time management.
    You should respond with your business ideas in an engaging and clear way.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.7

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OllamaChatCompletionClient(model='llama3.2', temperature=1.5)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source='user')
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my business idea. Please refine and enhance it for a more polished presentation. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)
