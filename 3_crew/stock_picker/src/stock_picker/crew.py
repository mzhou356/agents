from __future__ import annotations

import os
from typing import List

from crewai import Agent
from crewai import Crew
from crewai import Process
from crewai import Task
from crewai.memory import EntityMemory
from crewai.memory import LongTermMemory
from crewai.memory import ShortTermMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.project import agent
from crewai.project import crew
from crewai.project import CrewBase
from crewai.project import task
from crewai_tools import SerperDevTool
from pydantic import BaseModel
from pydantic import Field

from .tools.push_tool import PushNotificationTool


class TrendingCompany(BaseModel):
    """ A company that is in the news and attracting attention """
    name: str = Field(description='Company name')
    ticker: str = Field(description='Stock ticker symbol')
    reason: str = Field(
        description='Reason this company is trending in the news',
    )


class TrendingCompanyList(BaseModel):
    """ List of multiple trending companies that are in the news """
    companies: List[TrendingCompany] = Field(
        description='List of companies trending in the news',
    )


class TrendingCompanyResearch(BaseModel):
    """ Detailed research on a company """
    name: str = Field(description='Company name')
    market_position: str = Field(
        description='Current market position and competitive analysis',
    )
    future_outlook: str = Field(
        description='Future outlook and growth prospects',
    )
    investment_potential: str = Field(
        description='Investment potential and suitability for investment',
    )


class TrendingCompanyResearchList(BaseModel):
    """ A list of detailed research on all the companies """
    research_list: List[TrendingCompanyResearch] = Field(
        description='Comprehensive research on all trending companies',
    )


@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['trending_company_finder'],
            tools=[SerperDevTool()], memory=True,
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'],
            tools=[SerperDevTool()],
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker'],
            tools=[PushNotificationTool()], memory=True,
        )

    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'],
            output_pydantic=TrendingCompanyList,
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'],
            output_pydantic=TrendingCompanyResearchList,
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""

        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True,
        )

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            max_rpm=8,
            memory=True,
            # Long-term memory for persistent storage across sessions
            long_term_memory=LongTermMemory(
                storage=LTMSQLiteStorage(
                    db_path='./memory/long_term_memory_storage.db',
                ),
            ),
            # Short-term memory for current context using RAG
            short_term_memory=ShortTermMemory(
                storage=RAGStorage(
                    embedder_config={
                        'provider': 'huggingface',
                        'config': {
                            'model': 'sentence-transformers/all-mpnet-base-v2',
                            # "api key": os.environ["HF_TOKEN"],
                            'api_url': 'https://api-inference.huggingface.co',
                        },
                    },
                    type='short_term',
                    path='./memory/',
                ),
            ),            # Entity memory for tracking key information about entities
            entity_memory=EntityMemory(
                storage=RAGStorage(
                    embedder_config={
                        'provider': 'huggingface',
                        'config': {
                            'model': 'sentence-transformers/all-mpnet-base-v2',
                            # "api key": os.environ["HF_TOKEN"],
                            'api_url': 'https://api-inference.huggingface.co',
                        },
                    },
                    type='short_term',
                    path='./memory/',
                ),
            ),
        )
