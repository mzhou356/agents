# src/financial_researcher/crew.py
from __future__ import annotations

from crewai import Agent
from crewai import Crew
from crewai import Process
from crewai import Task
from crewai.project import agent
from crewai.project import crew
from crewai.project import CrewBase
from crewai.project import task
from crewai_tools import SerperDevTool


@CrewBase
class ResearchCrew():
    """Research crew for comprehensive topic analysis and reporting"""
    agents_config = 'config/agents.yaml'
    task_config = 'config/tasks.yaml'

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            tools=[SerperDevTool()],
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'],
            verbose=True,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            output_file='output/report.md',
        )

    @crew
    def crew(self) -> Crew:
        """Creates the research crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
