from abc import ABC, abstractmethod

import amqp

from .signals import message_started, message_finished


class EDAConsumer(ABC):  # pragma: no cover
    _message: amqp.Message

    def handle(self, message: amqp.Message):
        self._message = message

        message_started.send(sender=self)
        try:
            self.consume(message)
        except Exception as exception:
            message.channel.basic_reject(message.delivery_tag, requeue=False)
            print(f"[{self.__class__.__name__}] - Message rejected by: {exception}")
        finally:
            message_finished.send(sender=self)

    def ack(self):
        self._message.channel.basic_ack(self._message.delivery_tag)

    @abstractmethod
    def consume(self, message: amqp.Message):
        pass
