from aws_lambda_powertools import Logger

from .clisechubman import _apply_rules

LOGGER = Logger()


@LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: object) -> None:
    """Lambda handler to apply suppression rules to Security Hub findings."""
    _apply_rules()
