import logging
from abc import ABC, abstractmethod

import amqp

from weni.eda.parsers import JSONParser
from .signals import message_started, message_finished


class EDAConsumer(ABC):  # pragma: no cover
    _message: amqp.Message
    _parsed_body: dict = None
    _auto_ack_enabled: bool = True

    @property
    def logger(self):
        """Get logger instance for this consumer."""
        return logging.getLogger(f"eda.{self.__class__.__name__}")

    @property
    def body(self) -> dict:
        """
        Parse and return message body as dict.
        
        The body is parsed once and cached for subsequent access.
        """
        if self._parsed_body is None:
            self._parsed_body = JSONParser.parse(self._message.body)
        return self._parsed_body

    @property
    def message_body(self) -> bytes:
        """Raw message body."""
        return self._message.body

    @property
    def delivery_tag(self):
        """Message delivery tag."""
        return self._message.delivery_tag

    def handle(self, message: amqp.Message):
        self._message = message
        self._parsed_body = None  # Reset parsed body for new message

        message_started.send(sender=self)
        try:
            self.consume(message)
            # Auto-ack if consume() completed without exception
            if self._auto_ack_enabled:
                self.ack()
        except Exception as exception:
            message.channel.basic_reject(message.delivery_tag, requeue=False)
            self.logger.error(
                "Message rejected",
                extra={
                    "consumer": self.__class__.__name__,
                    "error": str(exception),
                    "body": message.body.decode("utf-8", errors="replace") if message.body else None,
                },
                exc_info=True,
            )
        finally:
            message_finished.send(sender=self)

    def ack(self):
        """Acknowledge the message."""
        self._message.channel.basic_ack(self._message.delivery_tag)

    @abstractmethod
    def consume(self, message: amqp.Message):
        pass
