"""Base Agent class."""


class Agent:
    """Base class for creating agents."""

    def __init__(self, name: str | None = None):
        self.name = name

    def run(self):
        """Run the agent."""
        raise NotImplementedError
