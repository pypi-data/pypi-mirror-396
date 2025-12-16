"""Type stubs for fast_decision"""

class FastDecision:
    """High-performance rule engine with MongoDB-style query syntax"""

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

    def execute(self, data: dict, categories: list[str]) -> list[str]:
        """
        Execute rules and return list of triggered rule IDs.

        Args:
            data: Input data as Python dict
            categories: List of category names to evaluate

        Returns:
            List of triggered rule IDs
        """
        ...

    def execute_json(self, data_json: str, categories: list[str]) -> list[str]:
        """
        Execute rules from JSON string.

        Args:
            data_json: Input data as JSON string
            categories: List of category names to evaluate

        Returns:
            List of triggered rule IDs

        Raises:
            ValueError: If JSON is invalid
        """
        ...

__all__ = ["FastDecision"]
