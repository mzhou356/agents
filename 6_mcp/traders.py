from __future__ import annotations

import json
import os
from contextlib import AsyncExitStack

from accounts_client import read_accounts_resource
from accounts_client import read_strategy_resource
from agents import Agent
from agents import OpenAIChatCompletionsModel
from agents import Runner
from agents import Tool
from agents import trace
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv
from mcp_params import researcher_mcp_server_params
from mcp_params import trader_mcp_server_params
from openai import AsyncOpenAI
from templates import rebalance_message
from templates import research_tool
from templates import researcher_instructions
from templates import trade_message
from templates import trader_instructions
from tracers import make_trace_id

load_dotenv(override=True)

from agents import set_tracing_export_api_key
set_tracing_export_api_key(os.environ['open_api_key'])

# deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
google_api_key = os.getenv('gemini_api_key')
# grok_api_key = os.getenv("GROK_API_KEY")
# openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
# GROK_BASE_URL = "https://api.x.ai/v1"
GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/openai/'
# OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

MAX_TURNS = 5

# openrouter_client = AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=openrouter_api_key)
# deepseek_client = AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=deepseek_api_key)
# grok_client = AsyncOpenAI(base_url=GROK_BASE_URL, api_key=grok_api_key)
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)


def get_model(model_name: str):
    # if "/" in model_name:
    #     return OpenAIChatCompletionsModel(model=model_name, openai_client=openrouter_client)
    # elif "deepseek" in model_name:
    #     return OpenAIChatCompletionsModel(model=model_name, openai_client=deepseek_client)
    # elif "grok" in model_name:
    #     return OpenAIChatCompletionsModel(model=model_name, openai_client=grok_client)
    # elif "gemini" in model_name:
    return OpenAIChatCompletionsModel(model=model_name, openai_client=gemini_client)
    # else:
    #     return model_name


async def get_researcher(mcp_servers, model_name) -> Agent:
    researcher = Agent(
        name='Researcher',
        instructions=researcher_instructions(),
        model=get_model(model_name),
        mcp_servers=mcp_servers,
    )
    return researcher


async def get_researcher_tool(mcp_servers, model_name) -> Tool:
    researcher = await get_researcher(mcp_servers, model_name)
    return researcher.as_tool(tool_name='Researcher', tool_description=research_tool())


class Trader:
    def __init__(self, name: str, lastname='Trader', model_name='gemini-2.0-flash'):
        self.name = name
        self.lastname = lastname
        self.agent = None
        self.model_name = model_name
        self.do_trade = True

    async def create_agent(self, trader_mcp_servers, researcher_mcp_servers) -> Agent:
        tool = await get_researcher_tool(researcher_mcp_servers, self.model_name)
        self.agent = Agent(
            name=self.name,
            instructions=trader_instructions(self.name),
            model=get_model(self.model_name),
            tools=[tool],
            mcp_servers=trader_mcp_servers,
        )
        return self.agent

    async def get_account_report(self) -> str:
        account = await read_accounts_resource(self.name)
        account_json = json.loads(account)
        account_json.pop('portfolio_value_time_series', None)
        return json.dumps(account_json)

    async def run_agent(self, trader_mcp_servers, researcher_mcp_servers):
        self.agent = await self.create_agent(trader_mcp_servers, researcher_mcp_servers)
        account = await self.get_account_report()
        strategy = await read_strategy_resource(self.name)
        message = (
            trade_message(self.name, strategy, account)
            if self.do_trade
            else rebalance_message(self.name, strategy, account)
        )
        await Runner.run(self.agent, message, max_turns=MAX_TURNS)

    async def run_with_mcp_servers(self):
        async with AsyncExitStack() as stack:
            trader_mcp_servers = [
                await stack.enter_async_context(
                    MCPServerStdio(params, client_session_timeout_seconds=120),
                )
                for params in trader_mcp_server_params
            ]
            async with AsyncExitStack() as stack:
                researcher_mcp_servers = [
                    await stack.enter_async_context(
                        MCPServerStdio(params, client_session_timeout_seconds=120),
                    )
                    for params in researcher_mcp_server_params(self.name)
                ]
                await self.run_agent(trader_mcp_servers, researcher_mcp_servers)

    async def run_with_trace(self):
        trace_name = f"{self.name}-trading" if self.do_trade else f"{self.name}-rebalancing"
        trace_id = make_trace_id(f"{self.name.lower()}")
        with trace(trace_name, trace_id=trace_id):
            await self.run_with_mcp_servers()

    async def run(self):
        try:
            await self.run_with_trace()
        except Exception as e:
            print(f"Error running trader {self.name}: {e}")
        self.do_trade = not self.do_trade
