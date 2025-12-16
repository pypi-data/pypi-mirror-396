"""
Rules Loader - Simplified replacement for Stage 3

Loads OWASP LLM Top 10 2025 rules from YAML file to provide context to the SLM.
Replaces the vector database approach with direct rule loading.
"""

from pathlib import Path
from typing import Any, Optional

import yaml


class RulesLoader:
    """
    Load and manage OWASP LLM security rules.

    Provides the comprehensive OWASP LLM Top 10 2025 rules that will be
    passed to the SLM analyzer as context for intelligent vulnerability detection.
    """

    def __init__(self, rules_path: Optional[Path] = None):
        """
        Initialize the rules loader.

        Args:
            rules_path: Path to the OWASP rules YAML file
        """
        if rules_path is None:
            # Default to rules directory in package
            package_root = Path(__file__).parent.parent
            rules_path = package_root / "rules" / "owasp_llm_top10_guide.yaml"

        self.rules_path = rules_path
        self._rules = None
        self._initialized = False

    def initialize(self) -> None:
        """Load the rules from YAML file."""
        if self._initialized:
            return

        if not self.rules_path.exists():
            raise FileNotFoundError(
                f"OWASP rules file not found: {self.rules_path}\n"
                f"Please ensure the rules file is included in the package."
            )

        with open(self.rules_path, encoding='utf-8') as f:
            self._rules = yaml.safe_load(f)

        self._initialized = True

    def get_rules(self) -> dict[str, Any]:
        """
        Get the complete OWASP rules dictionary.

        Returns:
            Dictionary containing all OWASP LLM Top 10 2025 rules
        """
        if not self._initialized:
            self.initialize()

        return self._rules

    def get_rules_as_text(self) -> str:
        """
        Get rules formatted as text for LLM context.

        Returns:
            Formatted string containing rules for SLM system prompt
        """
        if not self._initialized:
            self.initialize()

        # Convert YAML to readable text format for LLM
        rules_text = []
        rules_text.append("# OWASP LLM Top 10 2025 Security Rules")
        rules_text.append("")

        # Add OWASP categories
        if "owasp_categories" in self._rules:
            rules_text.append("## Vulnerability Categories:")
            rules_text.append("")

            for cat_id, category in self._rules["owasp_categories"].items():
                rules_text.append(f"### {cat_id}: {category.get('name', 'Unknown')}")

                if "description" in category:
                    rules_text.append(category["description"].strip())
                    rules_text.append("")

                # Add common vulnerabilities
                if "common_vulnerabilities" in category:
                    rules_text.append("**Common Vulnerabilities:**")
                    for vuln in category["common_vulnerabilities"]:
                        rules_text.append(f"- **{vuln.get('type', 'UNKNOWN')}** ({vuln.get('severity', 'MEDIUM')})")
                        rules_text.append(f"  {vuln.get('description', '')}")
                        rules_text.append("")

                rules_text.append("---")
                rules_text.append("")

        # Add detection guidelines
        if "detection_guidelines" in self._rules:
            rules_text.append("## Detection Guidelines:")
            rules_text.append("")
            guidelines = self._rules["detection_guidelines"]

            if "high_priority_checks" in guidelines:
                rules_text.append("**High Priority Checks:**")
                for check in guidelines["high_priority_checks"]:
                    rules_text.append(f"- {check}")
                rules_text.append("")

        return "\n".join(rules_text)

    def get_category_rules(self, category_id: str) -> Optional[dict[str, Any]]:
        """
        Get rules for a specific OWASP category.

        Args:
            category_id: OWASP category ID (e.g., "LLM01", "LLM02")

        Returns:
            Dictionary containing rules for that category, or None if not found
        """
        if not self._initialized:
            self.initialize()

        categories = self._rules.get("owasp_categories", {})
        return categories.get(category_id)

    def get_vulnerability_types(self) -> list:
        """
        Get a list of all vulnerability types across all categories.

        Returns:
            List of vulnerability type names
        """
        if not self._initialized:
            self.initialize()

        vuln_types = []
        categories = self._rules.get("owasp_categories", {})

        for category in categories.values():
            if "common_vulnerabilities" in category:
                for vuln in category["common_vulnerabilities"]:
                    if "type" in vuln:
                        vuln_types.append(vuln["type"])

        return vuln_types

    def get_detection_guidelines(self) -> dict[str, Any]:
        """
        Get the detection guidelines section.

        Returns:
            Dictionary containing detection guidelines
        """
        if not self._initialized:
            self.initialize()

        return self._rules.get("detection_guidelines", {})

    @property
    def is_loaded(self) -> bool:
        """Check if rules are loaded."""
        return self._initialized

    @property
    def rule_count(self) -> int:
        """Get the number of OWASP categories loaded."""
        if not self._initialized:
            return 0

        categories = self._rules.get("owasp_categories", {})
        return len(categories)
