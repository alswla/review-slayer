"""CrewAI 에이전트 생성 — 캐릭터 × 역할 조합.

역할(Role)이 무엇을 리뷰할지 결정하고,
캐릭터(Character)가 어떤 성격/말투로 리뷰할지 결정합니다.
"""

from __future__ import annotations

from crewai import Agent

from app.crew.characters import HashiraCharacter, get_character
from app.crew.config import ReviewCrewConfig, ReviewerAssignment
from app.crew.roles import ReviewRole, get_role


def create_agent(assignment: ReviewerAssignment) -> Agent:
    """Create a CrewAI agent from a role-character assignment.

    Args:
        assignment: A ReviewerAssignment with role_id and character_id.

    Returns:
        A CrewAI Agent with the character's personality and role's review focus.
    """
    role = get_role(assignment.role_id)
    character = get_character(assignment.character_id)

    return Agent(
        role=f"{character.icon} {character.name_ko} — {role.name}",
        goal=_build_goal(role, character),
        backstory=_build_backstory(role, character),
        verbose=False,
        allow_delegation=False,
    )


def create_agents_from_config(config: ReviewCrewConfig) -> list[Agent]:
    """Create all agents based on the review crew configuration.

    Args:
        config: Parsed ReviewCrewConfig with role-character assignments.

    Returns:
        List of CrewAI Agents, one per active role.
    """
    return [create_agent(assignment) for assignment in config.assignments]


def _build_goal(role: ReviewRole, character: HashiraCharacter) -> str:
    """Build the agent's goal combining role focus and character personality."""
    focus_list = "\n".join(f"  - {area}" for area in role.focus_areas)

    return (
        f"{role.goal}\n\n"
        f"집중 분석 영역:\n{focus_list}\n\n"
        f"리뷰 결과를 {character.name_ko}의 성격과 말투로 전달하세요.\n"
        f"{character.speaking_style}"
    )


def _build_backstory(role: ReviewRole, character: HashiraCharacter) -> str:
    """Build the agent's backstory combining character lore and role expertise."""
    return (
        f"당신은 귀멸의 칼날의 {character.breathing} 사용자, "
        f"{character.name_ko}({character.name_jp})입니다.\n"
        f"{character.personality}\n\n"
        f"당신의 전문 분야는 {role.name}이며, "
        f"코드 리뷰에서 {role.icon} {role.name} 관점으로 분석합니다.\n"
        f"항상 한국어로 리뷰하며, 당신의 캐릭터 성격에 맞는 말투를 사용합니다.\n"
        f"입버릇: \"{character.catchphrase}\""
    )
