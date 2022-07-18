from typing import Dict

from behave import step, use_step_matcher
from behave.runner import Context
from clients.rabbitmq_client import RABBITMQ_MESSAGES, get_rabbitmq_message
from she_logging import logger

use_step_matcher("re")


@step(
    f'an? "(?P<message_type>.+)" (?P<message_name>\w+_MESSAGE) message is published to RabbitMQ'
)
def message_published_to_rabbitmq(
    context: Context, message_type: str, message_name: str
) -> None:
    message: Dict = get_rabbitmq_message(context, RABBITMQ_MESSAGES[message_name])
    logger.debug("RabbitMQ message: %s", message)
    assert "event_type" in message
    assert message_type == message["event_type"]
