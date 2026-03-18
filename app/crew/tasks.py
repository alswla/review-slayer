"""CrewAI 태스크 정의 — 역할 기반 리뷰 + 교차 검증.

각 에이전트(역할×캐릭터)에 대해 리뷰 태스크를 생성하고,
모든 리뷰가 끝나면 교차 검증(토론) 태스크로 결과를 종합합니다.
"""

from __future__ import annotations

from crewai import Agent, Task

from app.crew.characters import get_character
from app.crew.config import ReviewerAssignment
from app.crew.roles import get_role


def create_review_task(
    agent: Agent,
    assignment: ReviewerAssignment,
    diff_text: str,
    pr_title: str,
) -> Task:
    """Create a review task for a specific agent.

    Args:
        agent: The CrewAI agent to assign the task to.
        assignment: The role-character assignment for this agent.
        diff_text: Formatted diff text to review.
        pr_title: PR title for context.

    Returns:
        A CrewAI Task instance.
    """
    role = get_role(assignment.role_id)
    character = get_character(assignment.character_id)
    focus_list = "\n".join(f"  - {area}" for area in role.focus_areas)

    return Task(
        description=(
            f"당신은 {character.icon} {character.name_ko}입니다.\n"
            f'PR 제목: "{pr_title}"\n\n'
            f"아래 코드 변경사항(diff)을 **{role.name}** 관점에서 리뷰하세요.\n\n"
            f"집중 분석 영역:\n{focus_list}\n\n"
            f"--- DIFF START ---\n{diff_text}\n--- DIFF END ---\n\n"
            f"## 리뷰 작성 규칙\n"
            f"1. {character.name_ko}의 성격과 말투로 리뷰하세요\n"
            f"2. 각 발견 사항에 아래 정보를 포함하세요:\n"
            f"   - **심각도**: 🔴 Critical / 🟡 Warning / 🟢 Suggestion / 🔵 Info\n"
            f"   - **파일**: 해당 파일명\n"
            f"   - **설명**: 문제에 대한 설명 ({character.name_ko}의 말투로)\n"
            f"   - **수정 제안**: 구체적인 해결 방법\n"
            f"3. 문제가 없으면 {character.name_ko}답게 칭찬하세요\n"
            f"4. 입버릇: \"{character.catchphrase}\"\n"
        ),
        expected_output=(
            f"{character.icon} {character.name_ko}의 {role.name} 리뷰 결과.\n"
            f"심각도별로 정리된 발견 사항 목록 (Markdown 형식).\n"
            f"{character.name_ko}의 캐릭터 성격에 맞는 말투 사용."
        ),
        agent=agent,
    )


def create_synthesis_task(
    agent: Agent,
    review_tasks: list[Task],
) -> Task:
    """Create a synthesis task that consolidates all reviews.

    This task takes all individual review results and creates
    a final, prioritised, well-organised report.

    Args:
        agent: The agent to run the synthesis.
        review_tasks: Previously completed review tasks.

    Returns:
        A CrewAI Task for cross-validation.
    """
    return Task(
        description=(
            "당신은 주(柱)들의 리뷰를 총괄하는 역할입니다.\n\n"
            "여러 주(柱)들의 코드 리뷰 결과가 주어집니다.\n"
            "이를 하나의 통합 보고서로 정리하세요.\n\n"
            "## 정리 규칙\n"
            "1. 모든 발견 사항을 심각도 순으로 정렬 (🔴→🟡→🟢→🔵)\n"
            "2. 파일별로 그룹핑\n"
            "3. 중복된 지적은 하나로 통합\n"
            "4. 상충되는 의견은 양쪽 모두 표시\n"
            "5. 각 주(柱)의 아이콘과 이름을 유지\n"
            "6. 상단에 간결한 요약 (2-3문장)\n"
            "7. 각 주의 말투/성격은 그대로 유지\n\n"
            "## 출력 형식\n"
            "```\n"
            "### 📋 요약\n"
            "[2-3문장 요약]\n\n"
            "### 🔴 Critical\n"
            "[주 아이콘] [주 이름]: [발견 내용]\n\n"
            "### 🟡 Warning\n"
            "...\n\n"
            "### 🟢 Suggestion\n"
            "...\n\n"
            "### 🔵 Info\n"
            "...\n"
            "```"
        ),
        expected_output=(
            "심각도별로 정리된 통합 코드 리뷰 보고서.\n"
            "Markdown 형식, 각 주(柱)의 아이콘과 캐릭터 말투 유지.\n"
            "한국어로 작성."
        ),
        agent=agent,
        context=review_tasks,
    )
