import logging
from abc import ABC, abstractmethod

import pika

from weni.eda.parsers import JSONParser
from .signals import message_started, message_finished


class PikaEDAConsumer(ABC):  # pragma: no cover
    _channel: pika.channel.Channel
    _method: pika.spec.Basic.Deliver
    _properties: pika.spec.BasicProperties
    _body: bytes
    _parsed_body: dict = None
    _auto_ack_enabled: bool = True

    @property
    def logger(self):
        """Get logger instance for this consumer."""
        return logging.getLogger(f"pika_eda.{self.__class__.__name__}")

    @property
    def body(self) -> dict:
        """
        Parse and return message body as dict.
        
        The body is parsed once and cached for subsequent access.
        """
        if self._parsed_body is None:
            self._parsed_body = JSONParser.parse(self._body)
        return self._parsed_body

    @property
    def message_body(self) -> bytes:
        """Raw message body."""
        return self._body

    @property
    def delivery_tag(self):
        """Message delivery tag."""
        return self._method.delivery_tag

    def handle(self, channel: pika.channel.Channel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes):
        self._channel = channel
        self._method = method
        self._properties = properties
        self._body = body
        self._parsed_body = None  # Reset parsed body for new message

        message_started.send(sender=self)
        try:
            self.consume(channel, method, properties, body)
            # Auto-ack if consume() completed without exception
            if self._auto_ack_enabled:
                self.ack()
        except Exception as exception:
            channel.basic_reject(method.delivery_tag, requeue=False)
            self.logger.error(
                "Message rejected",
                extra={
                    "consumer": self.__class__.__name__,
                    "error": str(exception),
                    "body": body.decode("utf-8", errors="replace") if body else None,
                },
                exc_info=True,
            )
        finally:
            message_finished.send(sender=self)

    def ack(self):
        """Acknowledge the message."""
        self._channel.basic_ack(self._method.delivery_tag)

    @abstractmethod
    def consume(self, channel: pika.channel.Channel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes):
        pass
