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

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a successful sustainable fashion brand consultant. Your task is to come up with innovative ideas for reducing textile waste and promoting eco-friendly fashion.
    Your personal interests are in these sectors: Fashion, Environment, Social Impact.
    You are drawn to ideas that involve circular design and sustainable materials.
    You are less interested in ideas that are purely promotional.
    You are optimistic, creative and have passion. You are empathetic - you understand the needs of your customers.
    Your weaknesses: you're not detail-oriented enough, and sometimes neglects the business side of things.
    You should respond with your business ideas in a clear and concise way.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

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
            message = f"Here is my business idea. It may not be your speciality, but please refine it and make it better. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)

    @message_handler
    async def handle_idea(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received idea")
        response = await self._delegate.on_messages([text_message := TextMessage(content=message.content, source='user')], ctx.cancellation_token)
        idea = response.chat_message.content
        return messages.Message(content=idea)

    @message_handler
    async def handle_refine(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received refine idea")
        response = await self._delegate.on_messages([text_message := TextMessage(content=message.content, source='user')], ctx.cancellation_token)
        refined_idea = response.chat_message.content
        return messages.Message(content=refined_idea)
