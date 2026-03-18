"""Webhook event handlers.

Each handler runs as a background task triggered by the webhook endpoint.
"""

import logging

from app.crew.config import ReviewCrewConfig, get_default_config, parse_config_yaml
from app.crew.crew import ReviewCrew
from app.github.client import GitHubClient
from app.github.comment import format_review_comment
from app.github.diff import parse_diff

logger = logging.getLogger(__name__)


async def handle_pull_request_event(payload: dict) -> None:
    """Handle pull_request opened / synchronize / reopened events.

    Flow:
        1. Extract PR metadata from webhook payload
        2. Fetch diff via GitHub API
        3. Load .review-slayer.yml config from repo (if exists)
        4. Parse diff into structured data
        5. Run CrewAI review agents (selected Hashira)
        6. Format results and post comment to PR
    """
    try:
        # ── Extract metadata ──
        pr = payload["pull_request"]
        repo_full_name = payload["repository"]["full_name"]
        pr_number = pr["number"]
        installation_id = payload["installation"]["id"]

        logger.info("🗡️ Starting Hashira review for %s #%d", repo_full_name, pr_number)

        # ── Fetch diff ──
        gh = GitHubClient(installation_id=installation_id)
        diff_text = await gh.get_pull_request_diff(repo_full_name, pr_number)

        if not diff_text.strip():
            logger.info("Empty diff for %s #%d — skipping review", repo_full_name, pr_number)
            return

        # ── Load repo config (.review-slayer.yml) ──
        config = await _load_repo_config(gh, repo_full_name)

        # ── Parse diff ──
        diff_files = parse_diff(diff_text)
        logger.info("Parsed %d files from diff", len(diff_files))

        # ── Run CrewAI review with Hashira agents ──
        crew = ReviewCrew(config=config)
        review_result = crew.run_review(diff_files=diff_files, pr_title=pr.get("title", ""))

        # ── Post comment ──
        comment_body = format_review_comment(review_result, config)
        await gh.create_review_comment(repo_full_name, pr_number, comment_body)

        logger.info("⚔️ Hashira review posted for %s #%d", repo_full_name, pr_number)

    except Exception:
        logger.exception("❌ Failed to process PR review for payload")


async def _load_repo_config(gh: GitHubClient, repo: str) -> ReviewCrewConfig:
    """Try to load .review-slayer.yml from the repository.

    Args:
        gh: Authenticated GitHub client.
        repo: Full repository name.

    Returns:
        Parsed config, or default config if file not found.
    """
    try:
        content = await gh.get_file_content(repo, ".review-slayer.yml")
        if content:
            logger.info("Loaded .review-slayer.yml from %s", repo)
            return parse_config_yaml(content)
    except Exception:
        logger.debug("No .review-slayer.yml found in %s — using defaults", repo)

    return get_default_config()
