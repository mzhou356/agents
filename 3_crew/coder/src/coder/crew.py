from __future__ import annotations

from crewai import Agent
from crewai import Crew
from crewai import Process
from crewai import Task
from crewai.project import agent
from crewai.project import crew
from crewai.project import CrewBase
from crewai.project import task


@CrewBase
class Coder():
    """Coder crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # One click install for Docker Desktop:
    # https://docs.docker.com/desktop/

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config['coder'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode='safe',  # Uses Docker for safety
            max_execution_time=30,
            max_retry_limit=3,
        )

    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config['coding_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Coder crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=8,
        )
