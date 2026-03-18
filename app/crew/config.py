"""Review Slayer 설정 관리.

.review-slayer.yml 파일을 파싱하여 어떤 역할을 어떤 캐릭터가 수행할지 결정합니다.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import yaml

from app.crew.characters import ALL_CHARACTERS, get_character
from app.crew.roles import ALL_ROLES, DEFAULT_ROLE_IDS, get_role

logger = logging.getLogger(__name__)


@dataclass
class ReviewerAssignment:
    """A single role-character assignment."""

    role_id: str
    character_id: str


@dataclass
class ReviewCrewConfig:
    """Parsed review crew configuration."""

    assignments: list[ReviewerAssignment] = field(default_factory=list)

    @property
    def active_roles(self) -> list[str]:
        """Return list of active role IDs."""
        return [a.role_id for a in self.assignments]

    @property
    def active_characters(self) -> list[str]:
        """Return list of active character IDs."""
        return [a.character_id for a in self.assignments]


def parse_config_yaml(yaml_content: str) -> ReviewCrewConfig:
    """Parse a .review-slayer.yml file content into ReviewCrewConfig.

    Expected format:
        reviewers:
          security: shinobu
          performance: muichiro
          bug_detection: sanemi  # override default rengoku

    Args:
        yaml_content: Raw YAML string.

    Returns:
        Parsed ReviewCrewConfig with validated assignments.
    """
    try:
        data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        logger.warning("Failed to parse .review-slayer.yml: %s — using defaults", e)
        return get_default_config()

    if not isinstance(data, dict):
        return get_default_config()

    reviewers = data.get("reviewers", {})
    if not isinstance(reviewers, dict):
        return get_default_config()

    assignments = []
    for role_id, character_id in reviewers.items():
        # Validate role
        if role_id not in ALL_ROLES:
            logger.warning("Unknown role '%s' in config — skipping", role_id)
            continue

        # Validate character
        character_id = str(character_id).lower()
        role = get_role(role_id)

        if character_id not in ALL_CHARACTERS:
            logger.warning(
                "Unknown character '%s' for role '%s' — using primary '%s'",
                character_id,
                role_id,
                role.primary_character,
            )
            character_id = role.primary_character

        # Validate character is allowed for this role (primary or secondary)
        if character_id not in (role.primary_character, role.secondary_character):
            logger.warning(
                "Character '%s' is not available for role '%s' "
                "(options: %s, %s) — using primary",
                character_id,
                role_id,
                role.primary_character,
                role.secondary_character,
            )
            character_id = role.primary_character

        assignments.append(ReviewerAssignment(role_id=role_id, character_id=character_id))

    if not assignments:
        return get_default_config()

    return ReviewCrewConfig(assignments=assignments)


def get_default_config() -> ReviewCrewConfig:
    """Return default configuration with 5 core roles and primary characters."""
    assignments = []
    for role_id in DEFAULT_ROLE_IDS:
        role = get_role(role_id)
        assignments.append(
            ReviewerAssignment(role_id=role_id, character_id=role.primary_character)
        )
    return ReviewCrewConfig(assignments=assignments)


def get_full_config() -> ReviewCrewConfig:
    """Return configuration with ALL 9 roles and primary characters."""
    assignments = []
    for role_id, role in ALL_ROLES.items():
        assignments.append(
            ReviewerAssignment(role_id=role_id, character_id=role.primary_character)
        )
    return ReviewCrewConfig(assignments=assignments)


def get_config_help() -> str:
    """Generate help text showing available roles and characters."""
    lines = ["# .review-slayer.yml 설정 가이드", "", "reviewers:"]
    for role_id, role in ALL_ROLES.items():
        primary = get_character(role.primary_character)
        secondary = get_character(role.secondary_character)
        lines.append(
            f"  {role_id}: {role.primary_character}  "
            f"# {role.icon} {role.name} "
            f"(🥇 {primary.icon}{primary.name_ko} / 🥈 {secondary.icon}{secondary.name_ko})"
        )
    return "\n".join(lines)
