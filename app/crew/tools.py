"""Custom CrewAI tools for code review.

These tools give agents the ability to read and analyse diff data.
"""

from crewai.tools import BaseTool


class DiffReaderTool(BaseTool):
    """Tool that provides diff content to agents.

    The diff text is injected at creation time and the agent
    can call this tool to retrieve the full diff.
    """

    name: str = "diff_reader"
    description: str = (
        "Read the code diff for the current pull request. "
        "Returns the full unified diff with file changes, additions, and deletions."
    )
    diff_text: str = ""

    def _run(self, query: str = "") -> str:
        """Return the stored diff text."""
        if not self.diff_text:
            return "No diff data available."
        return self.diff_text
