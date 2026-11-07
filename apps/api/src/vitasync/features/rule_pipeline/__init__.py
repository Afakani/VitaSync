"""Rule pipeline: validated flags -> RuleResult (the rule JSON). Public API of this module."""
from vitasync.features.rule_pipeline.pipeline import check_rules

__all__ = ["check_rules"]
