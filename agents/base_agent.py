from agno.agent import Agent
from agno.models.groq import Groq
import os


class BaseAgent:
    def __init__(self, name, description, avatar="default_avatar.png"):

        self.name = name
        self.description = description
        self.avatar = avatar
        self.model = Groq(id="llama-3.3-70b-versatile")
        self.agent = Agent(model=self.model, markdown=True)

    def get_response(self, query, stream=False):

        return self.agent.get_response(query, stream=stream)

    def print_response(self, query, stream=True):

        return self.agent.print_response(query, stream=stream)