"""Unified diff parser.

Parses GitHub-style unified diff text into structured DiffFile objects
that can be consumed by CrewAI agents.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class DiffHunk:
    """A single hunk within a diff file."""

    header: str  # e.g. "@@ -10,5 +10,7 @@ def some_function():"
    changes: list[str] = field(default_factory=list)  # raw diff lines

    @property
    def added_lines(self) -> list[str]:
        return [line[1:] for line in self.changes if line.startswith("+")]

    @property
    def removed_lines(self) -> list[str]:
        return [line[1:] for line in self.changes if line.startswith("-")]


@dataclass
class DiffFile:
    """Represents a single file's changes in a diff."""

    filename: str
    status: str  # "added", "modified", "deleted", "renamed"
    hunks: list[DiffHunk] = field(default_factory=list)

    @property
    def total_additions(self) -> int:
        return sum(len(h.added_lines) for h in self.hunks)

    @property
    def total_deletions(self) -> int:
        return sum(len(h.removed_lines) for h in self.hunks)

    def to_text(self) -> str:
        """Convert to a human-readable text representation for agents."""
        lines = [f"=== {self.filename} ({self.status}) ==="]
        lines.append(f"  +{self.total_additions} -{self.total_deletions} lines")
        lines.append("")
        for hunk in self.hunks:
            lines.append(hunk.header)
            lines.extend(hunk.changes)
            lines.append("")
        return "\n".join(lines)


# ── Regex patterns ──
FILE_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+)$")
HUNK_HEADER_RE = re.compile(r"^@@\s.+?\s@@.*$")
DEV_NULL = "/dev/null"


def parse_diff(diff_text: str) -> list[DiffFile]:
    """Parse a unified diff string into a list of DiffFile objects.

    Args:
        diff_text: Raw unified diff text from GitHub API.

    Returns:
        List of DiffFile objects with parsed hunks and change lines.
    """
    files: list[DiffFile] = []
    current_file: DiffFile | None = None
    current_hunk: DiffHunk | None = None

    for line in diff_text.splitlines():
        # ── New file header ──
        file_match = FILE_HEADER_RE.match(line)
        if file_match:
            old_path, new_path = file_match.group(1), file_match.group(2)

            # Determine status
            status = "modified"
            filename = new_path
            # We'll refine status when we see --- and +++ lines
            current_file = DiffFile(filename=filename, status=status)
            current_hunk = None
            files.append(current_file)
            continue

        if current_file is None:
            continue

        # ── Detect added / deleted ──
        if line.startswith("--- "):
            old_name = line[4:].strip()
            if old_name == DEV_NULL or old_name == "/dev/null":
                current_file.status = "added"
            continue

        if line.startswith("+++ "):
            new_name = line[4:].strip()
            if new_name == DEV_NULL or new_name == "/dev/null":
                current_file.status = "deleted"
            # Update filename from +++ header (strip b/ prefix)
            if new_name.startswith("b/"):
                current_file.filename = new_name[2:]
            continue

        # ── Hunk header ──
        if HUNK_HEADER_RE.match(line):
            current_hunk = DiffHunk(header=line)
            current_file.hunks.append(current_hunk)
            continue

        # ── Diff content lines ──
        if current_hunk is not None and (
            line.startswith("+") or line.startswith("-") or line.startswith(" ")
        ):
            current_hunk.changes.append(line)

    return files


def diff_files_to_text(diff_files: list[DiffFile]) -> str:
    """Convert all diff files into a single text block for agent consumption."""
    parts = [f.to_text() for f in diff_files]
    summary = f"Total files changed: {len(diff_files)}\n"
    summary += f"Total additions: {sum(f.total_additions for f in diff_files)}\n"
    summary += f"Total deletions: {sum(f.total_deletions for f in diff_files)}\n"
    summary += "=" * 60 + "\n\n"
    return summary + "\n".join(parts)
