"""CrewAI 크루 조립 및 실행.

설정(ReviewCrewConfig)에 따라 선택된 주(柱)들로 크루를 구성하고,
리뷰 → 교차 검증 → 최종 보고서 순으로 실행합니다.
"""

from __future__ import annotations

import logging
import os

from crewai import Agent, Crew, Process

from app.config import get_settings
from app.crew.agents import create_agents_from_config
from app.crew.config import ReviewCrewConfig, ReviewerAssignment, get_default_config
from app.crew.tasks import create_review_task, create_synthesis_task
from app.github.diff import DiffFile, diff_files_to_text

logger = logging.getLogger(__name__)


class ReviewCrew:
    """Manages the CrewAI review workflow with Hashira agents."""

    def __init__(self, config: ReviewCrewConfig | None = None):
        """Initialize ReviewCrew.

        Args:
            config: Review configuration. If None, uses default 5-role config.
        """
        settings = get_settings()
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key

        self.config = config or get_default_config()

    def run_review(self, diff_files: list[DiffFile], pr_title: str = "") -> str:
        """Run the full review pipeline with configured Hashira agents.

        Args:
            diff_files: Parsed diff data.
            pr_title: Pull request title for context.

        Returns:
            The final consolidated review text.
        """
        diff_text = diff_files_to_text(diff_files)
        logger.info(
            "Starting review (diff: %d chars, agents: %d)",
            len(diff_text),
            len(self.config.assignments),
        )

        # ── Create agents from config ──
        agents = create_agents_from_config(self.config)

        # ── Create review tasks (one per agent) ──
        review_tasks = []
        for agent, assignment in zip(agents, self.config.assignments):
            task = create_review_task(
                agent=agent,
                assignment=assignment,
                diff_text=diff_text,
                pr_title=pr_title,
            )
            review_tasks.append(task)

        # ── Create synthesis agent + task ──
        synthesis_agent = Agent(
            role="📋 주(柱) 합동회의 — 리뷰 종합",
            goal="모든 주(柱)의 리뷰 결과를 통합하여 최종 보고서를 작성합니다.",
            backstory=(
                "당신은 귀살대의 당주(産屋敷耀哉)입니다. "
                "각 주(柱)들의 보고를 종합하여 최종 판단을 내리는 역할입니다. "
                "공정하고 지혜로운 시각으로 리뷰를 정리합니다. "
                "한국어로 작성하세요."
            ),
            verbose=False,
            allow_delegation=False,
        )

        synthesis_task = create_synthesis_task(
            agent=synthesis_agent,
            review_tasks=review_tasks,
        )

        # ── Assemble & kickoff ──
        all_agents = [*agents, synthesis_agent]
        all_tasks = [*review_tasks, synthesis_task]

        crew = Crew(
            agents=all_agents,
            tasks=all_tasks,
            process=Process.sequential,
            verbose=False,
        )

        agent_names = [a.role for a in agents]
        logger.info("Kicking off review crew: %s", agent_names)

        result = crew.kickoff()

        logger.info("Review crew completed")
        return str(result)
