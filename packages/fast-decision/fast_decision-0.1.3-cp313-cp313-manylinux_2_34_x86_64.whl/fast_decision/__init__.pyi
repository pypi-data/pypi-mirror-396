"""Type stubs for fast_decision"""

from typing import Any, TypedDict

class Rule(TypedDict):
    """Rule object returned by execute methods"""
    id: str
    priority: int
    conditions: dict[str, Any]
    action: str

class FastDecision:
    """High-performance rule engine"""

    def __init__(self, rules_path: str) -> None:
        """
        Load rules from JSON file.

        Args:
            rules_path: Path to JSON file with rules

        Raises:
            IOError: If file cannot be read
            ValueError: If JSON is invalid
        """
        ...

    def execute(self, data: dict, categories: list[str]) -> list[Rule]:
        """
        Execute rules and return list of triggered rule objects.

        Args:
            data: Input data as Python dict
            categories: List of category names to evaluate

        Returns:
            List of triggered rule objects, each containing:
                - id: Rule identifier
                - priority: Rule priority
                - conditions: Rule conditions
                - action: Rule action
        """
        ...

    def execute_json(self, data_json: str, categories: list[str]) -> list[Rule]:
        """
        Execute rules from JSON string.

        Args:
            data_json: Input data as JSON string
            categories: List of category names to evaluate

        Returns:
            List of triggered rule objects, each containing:
                - id: Rule identifier
                - priority: Rule priority
                - conditions: Rule conditions
                - action: Rule action

        Raises:
            ValueError: If JSON is invalid
        """
        ...

__all__ = ["FastDecision", "Rule"]
