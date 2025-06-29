from __future__ import annotations

import os

from agents import OpenAIChatCompletionsModel
from agents import set_tracing_export_api_key
from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv(override=True)

set_tracing_export_api_key(os.environ['open_api_key'])

google_api_key = os.getenv('gemini_api_key')
GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/openai/'
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)
gemini_model = OpenAIChatCompletionsModel(
    model='gemini-2.0-flash', openai_client=gemini_client,
)
