from __future__ import annotations

import os

from agents import Agent
from agents import function_tool
from agents import ModelSettings
from langchain_google_community import GoogleSearchAPIWrapper
from research_chat import gemini_model

google_search_client = GoogleSearchAPIWrapper(
    google_api_key=os.environ['google_search_key'], google_cse_id=os.environ['GOOGLE_CSE_ID'],
)


@function_tool
def google_search(query: str) -> str:
    """Search the web for information related to a query.
    Args:
        query: The search query

    Returns:
        Search results as text
    """
    try:
        result = google_search_client.run(query)
        return result
    except Exception as exc:
        return f"I couldn't perform the search due to a technical issue {exc}"


INSTRUCTIONS = (
    'You are a research assistant. Given a search term, you search the web for that term and '
    'produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 '
    'words. Capture the main points. Write succintly, no need to have complete sentences or good '
    'grammar. This will be consumed by someone synthesizing a report, so its vital you capture the '
    'essence and ignore any fluff. Do not include any additional commentary other than the summary itself.'
)


search_agent = Agent(
    name='Search agent',
    instructions=INSTRUCTIONS,
    tools=[google_search],
    model=gemini_model,
    model_settings=ModelSettings(tool_choice='required'),
)
