import logging


from pika.adapters.utils.connection_workflow import AMQPConnectorStackTimeout
from pika.exceptions import AMQPConnectionError

from .abstract_task_runner_strategy import AbstractTaskRunnerStrategy
from .. import AbstractDomainEventsService
from ...ioc import get_container
from ...utils import config, async_task


class PublishDomainEventStrategy(AbstractTaskRunnerStrategy):

    def __init__(self, exchange_name: str, countdown_delay: int = 10):
        self.exchange_name = exchange_name
        self.countdown_delay = countdown_delay

    @async_task(autoretry_for=(AMQPConnectionError,AMQPConnectorStackTimeout,))
    def _publish_to_exchange(self, message, routing_key, exchange = None):
        container = get_container()
        domain_events_service = container.get(AbstractDomainEventsService)
        domain_events_service.publish(message, event_type=routing_key, exchange=exchange)

    def run(self, *args, **kwargs):
        """
        Publish a domain event asynchronously.

        This method schedules a background task that publishes a message to the
        configured exchange after a configurable delay.

        Args:
            *args:
                - message (str): A JSON-formatted string representing the event payload.
                - event_type (DomainEvent): The event type used to route the message.
            **kwargs: Not used.
        """

        if len(args) < 2:
            raise ValueError("At least two arguments are required: message and event_type")

        message, event_type = args[0], args[1]

        if not isinstance(message, (dict, str)):
            raise ValueError("message must be either a dict or a string containing valid JSON")


        task = self._publish_to_exchange.apply_async(args=(message, event_type, self.exchange_name),
                                                     countdown=self.countdown_delay)

        (logging.getLogger('api')
         .info(f'PublishDomainEventStrategy::run - _publish_to_exchange.apply_async - new task {task.id}'))