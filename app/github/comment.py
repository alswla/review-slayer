"""Review comment formatter — 귀멸의 칼날 테마.

CrewAI 리뷰 결과를 주(柱) 테마의 GitHub Markdown 코멘트로 포맷합니다.
"""

from __future__ import annotations

from app.crew.characters import get_character
from app.crew.config import ReviewCrewConfig, get_default_config
from app.crew.roles import get_role


def format_review_comment(
    review_result: str,
    config: ReviewCrewConfig | None = None,
) -> str:
    """Format CrewAI review output into a Hashira-themed GitHub PR comment.

    Args:
        review_result: Raw text output from the CrewAI review crew.
        config: Review configuration (for listing active Hashira).

    Returns:
        A Markdown-formatted comment string.
    """
    config = config or get_default_config()
    body = _build_header(config)

    # Review result
    body += review_result + "\n\n"

    body += _build_footer(config)
    return body


def _build_header(config: ReviewCrewConfig) -> str:
    """Build the Hashira-themed comment header."""
    # Active Hashira badges
    hashira_badges = []
    for assignment in config.assignments:
        character = get_character(assignment.character_id)
        role = get_role(assignment.role_id)
        hashira_badges.append(f"{character.icon} **{character.name_ko}**({role.name})")

    badges_str = " · ".join(hashira_badges)

    return (
        "## ⚔️ Review Slayer — 주(柱) 합동 코드 리뷰\n\n"
        f"> {badges_str}\n\n"
        "---\n\n"
    )


def _build_footer(config: ReviewCrewConfig) -> str:
    """Build the themed comment footer."""
    count = len(config.assignments)
    return (
        "\n---\n"
        f"<sub>⚔️ <b>Review Slayer</b> — {count}명의 주(柱)가 리뷰했습니다 | "
        f"귀살대 AI 코드 리뷰</sub>\n"
    )


def format_summary_comment(
    total_files: int,
    total_additions: int,
    total_deletions: int,
    review_result: str,
    config: ReviewCrewConfig | None = None,
) -> str:
    """Format a summary review comment with stats header.

    Args:
        total_files: Number of files changed.
        total_additions: Total lines added.
        total_deletions: Total lines deleted.
        review_result: Raw text output from CrewAI review crew.
        config: Review configuration.

    Returns:
        A Markdown-formatted comment with summary stats.
    """
    config = config or get_default_config()
    body = _build_header(config)

    stats = (
        f"📊 **{total_files}** files changed "
        f"(**+{total_additions}** additions, **-{total_deletions}** deletions)\n\n"
    )
    body += stats + review_result + "\n\n"
    body += _build_footer(config)

    return body
