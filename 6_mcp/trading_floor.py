from __future__ import annotations

import asyncio
import os
from typing import List

from agents import add_trace_processor
from dotenv import load_dotenv
from market import is_market_open
from tracers import LogTracer
from traders import Trader

load_dotenv(override=True)

from agents import set_tracing_export_api_key
set_tracing_export_api_key(os.environ['open_api_key'])

RUN_EVERY_N_MINUTES = int(os.getenv('RUN_EVERY_N_MINUTES', '60'))
RUN_EVEN_WHEN_MARKET_IS_CLOSED = (
    os.getenv('RUN_EVEN_WHEN_MARKET_IS_CLOSED', 'false').strip().lower() == 'true'
)
USE_MANY_MODELS = os.getenv('USE_MANY_MODELS', 'false').strip().lower() == 'true'

names = ['Warren', 'Ray']
lastnames = ['Patience', 'Systematic']

if USE_MANY_MODELS:
    model_names = [
        'gpt-4.1-mini',
        'deepseek-chat',
        'gemini-2.5-flash-preview-04-17',
        'grok-3-mini-beta',
    ]
    short_model_names = ['GPT 4.1 Mini', 'DeepSeek V3', 'Gemini 2.5 Flash', 'Grok 3 Mini']
else:
    model_names = ['gemini-2.0-flash'] * 4
    short_model_names = ['GEMINI 2.0 FLash'] * 4


def create_traders() -> List[Trader]:
    traders = []
    for name, lastname, model_name in zip(names, lastnames, model_names):
        traders.append(Trader(name, lastname, model_name))
    return traders


async def run_every_n_minutes():
    add_trace_processor(LogTracer())
    traders = create_traders()
    while True:
        if RUN_EVEN_WHEN_MARKET_IS_CLOSED or is_market_open():
            await asyncio.gather(*[trader.run() for trader in traders])
        else:
            print('Market is closed, skipping run')
        await asyncio.sleep(RUN_EVERY_N_MINUTES * 60)


if __name__ == '__main__':
    print(f"Starting scheduler to run every {RUN_EVERY_N_MINUTES} minutes")
    asyncio.run(run_every_n_minutes())
