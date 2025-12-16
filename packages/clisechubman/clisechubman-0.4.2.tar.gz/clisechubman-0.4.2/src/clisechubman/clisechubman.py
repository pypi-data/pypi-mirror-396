import logging
from pathlib import Path

import yaml
from sechubman import Rule

logger = logging.getLogger(__name__)


def _validate_rules(rules_path: str = "rules.yaml") -> bool:
    with Path(rules_path).open() as file:
        rules = yaml.safe_load(file)["Rules"]

    all_valid = True

    for it, rule_dict in enumerate(rules, start=1):
        logger.info(f"Validating rule '{it}'")
        rule = Rule(**rule_dict)
        if rule.is_deep_validated:
            logger.info(
                f"Rule '{it}' with note '{rule.UpdatesToFilteredFindings['Note']['Text']}' is valid."
            )
        else:
            logger.error(f"Rule '{it}' is NOT valid.")
            all_valid = False

    return all_valid


def _apply_rules(rules_path: str = "rules.yaml") -> None:
    with Path(rules_path).open() as file:
        rules = yaml.safe_load(file)["Rules"]

    for it, rule_dict in enumerate(rules, start=1):
        logger.info(f"Applying rule '{it}'")
        rule = Rule(**rule_dict)
        rule.apply()
