import json
import logging
import random
import time
from typing import Any

import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from ..domain import DomainEvent, EventMessageFactory
from ..utils import config

from .abstract_event_dispatcher import AbstractEventDispatcher
from .abstract_domain_events_service import AbstractDomainEventsService


class AMQPService(AbstractDomainEventsService):
    def __init__(self,
                 event_dispatcher: AbstractEventDispatcher=None,
                 event_message_type: str=None,
                 exchange_name=None,
                 queue_name=None,
                 rabbit_host=config('RABBIT.HOST'),
                 rabbit_port=config('RABBIT.PORT'),
                 rabbit_username=config('RABBIT.USER'),
                 rabbit_password=config('RABBIT.PASSWORD'),
                 virtual_host=config('RABBIT.VIRTUAL_HOST'),
                 exchange_type=config('RABBIT.EXCHANGE_TYPE', 'direct'),
                 routing_keys=None,
                 max_retries=3,
                 base_delay=1.0,
                 max_delay=30.0,
                 jitter=True):

        self.rabbit_host = rabbit_host
        self.rabbit_port = rabbit_port
        self.virtual_host = virtual_host
        self.credentials = pika.PlainCredentials(rabbit_username, rabbit_password)

        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.queue_name = queue_name
        self.routing_keys = routing_keys or []
        self.connection = None
        self.channel = None

        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

        self.dispatcher = event_dispatcher
        self.event_message_type = event_message_type

    def _calculate_delay(self, attempt: int) -> float:
        """Calculates the delay with exponential backoff and optional jitter"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)

        if self.jitter:
            # Adds ±25% jitter to prevent thundering herd
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay)

    def _is_retryable_exception(self, exception: Exception) -> bool:
        """Determines whether an exception is recoverable"""
        retryable_exceptions = (
            AMQPConnectionError,
            ConnectionError,
            OSError,  # Includes network errors
            TimeoutError,
        )

        # Do not retry channel errors that indicate configuration problems
        non_retryable_exceptions = (
            AMQPChannelError,
        )

        if isinstance(exception, non_retryable_exceptions):
            return False

        return isinstance(exception, retryable_exceptions)

    def _is_valid_event(self, event_type: str) -> bool:
        try:
            return any(routing_key == event_type for routing_key in self.routing_keys)
        except:
            return False

    def _connect(self):
        """Establish connection and declare exchange/queue."""
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbit_host,
                                                                            port=self.rabbit_port,
                                                                            virtual_host=self.virtual_host,
                                                                            credentials=self.credentials))
        self.channel = self.connection.channel()


        # Declare a direct exchange
        if self.exchange_name:
            self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type, durable=True)

        # Declare a durable queue
        if self.queue_name:
            self.channel.queue_declare(queue=self.queue_name, durable=True)

        # Bind queue to all provided routing keys
        if self.exchange_name and self.queue_name:
            for key in self.routing_keys:
                self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=key)
                logging.getLogger('api').info(f"AMQPService::_connet: Queue {self.queue_name} bound to {key}")

    def _callback(self, ch, method, properties, body):
        """Process incoming messages depending on routing key."""
        logging.getLogger('api').info(f"Message received: {body} with routing_key={method.routing_key}")

        try:
            event = EventMessageFactory.create(self.event_message_type, ch, method, properties, body)

            # Validate it's a known event
            if not self._is_valid_event(event.event_type):
                logging.getLogger('api').warning(f"AMQPService::_callback: Unknown event type: {event.event_type}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # Process event
            success = True if not self.dispatcher else self.dispatcher.dispatch(event)

            if success:
                # Accept
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # Reject
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            logging.getLogger('api').error(f"AMQPService::_callback: Critical error processing message: {e}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def publish(self, message: Any, event_type: DomainEvent, exchange: str = None):
        rabbit_exchange = exchange if not exchange is None else self.exchange_name
        rabbit_routing_key = event_type if not event_type is None else config('RABBIT.DEFAULT_ROUTING_KEY')

        for attempt in range(self.max_retries + 1):
            cnn = None
            try:
                cnn = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbit_host,
                                                                        port=self.rabbit_port,
                                                                        virtual_host=self.virtual_host,
                                                                        credentials=self.credentials))
                channel = cnn.channel()
                channel.exchange_declare(exchange=rabbit_exchange, exchange_type=self.exchange_type, durable=True)

                message_body = json.dumps(message).encode('utf-8')

                channel.basic_publish(
                    exchange=rabbit_exchange,
                    routing_key=rabbit_routing_key,
                    body=message_body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # persistent message
                    ),
                )
                logging.getLogger('api').debug(
                    f'AMQPService::publish: Message sent to exchange {rabbit_exchange} using routing_key {rabbit_routing_key}')
                break

            except Exception as e:
                if attempt == self.max_retries:
                    # Last failed attempt
                    logging.getLogger('api').error(
                        f'Failed to publish message to {rabbit_exchange} after {self.max_retries + 1} attempts: {e}')
                    break

                if not self._is_retryable_exception(e):
                    # Unrecoverable error, do not retry
                    logging.getLogger('api').error(f'Failed to publish message to {rabbit_exchange}: {e}')
                    break

                # Calculate delay and retry
                delay = self._calculate_delay(attempt)
                logging.getLogger('api').warning(
                    f'Failed to publish message to {rabbit_exchange} '
                    f'(attempt {attempt + 1}/{self.max_retries + 1}): {e}. '
                    f'Retrying in {delay:.2f} seconds...'
                )
                time.sleep(delay)
            finally:
                if cnn and not cnn.is_closed:
                    try:
                        cnn.close()
                    except Exception as close_error:
                        logging.getLogger('api').error(f'Error closing connection: {close_error}')

    def subscribe(self):
        try:
            """Start listening messages from the queue."""
            if not self.channel:
                self._connect()

            if self.queue_name:
                self.channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self._callback
                )

            logging.getLogger('api').info("Waiting for messages...")
            self.channel.start_consuming()
        except Exception as e:
            logging.getLogger('api').error(f'AMQPService::subscribe: Failed to subscribe to {self.queue_name}: {e}')