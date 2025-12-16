from abc import ABC, abstractmethod

import pika

from .signals import message_started, message_finished


class PikaEDAConsumer(ABC):  # pragma: no cover
    _channel: pika.channel.Channel
    _method: pika.spec.Basic.Deliver
    _properties: pika.spec.BasicProperties
    _body: bytes

    def handle(self, channel: pika.channel.Channel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes):
        self._channel = channel
        self._method = method
        self._properties = properties
        self._body = body

        message_started.send(sender=self)
        try:
            self.consume(channel, method, properties, body)
        except Exception as exception:
            channel.basic_reject(method.delivery_tag, requeue=False)
            print(f"[{self.__class__.__name__}] - Message rejected by: {exception}")
        finally:
            message_finished.send(sender=self)

    def ack(self):
        self._channel.basic_ack(self._method.delivery_tag)

    @abstractmethod
    def consume(self, channel: pika.channel.Channel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes):
        pass
