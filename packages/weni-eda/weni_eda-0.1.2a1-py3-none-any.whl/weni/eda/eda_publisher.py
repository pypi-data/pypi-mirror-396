import json

import amqp

from .connection_params import ParamsFactory
from .connection import EDAConnection


class EDAPublisher:
    def __init__(self, connection_params_factory: ParamsFactory):
        self._connection_params = connection_params_factory.get_params()

    def send_message(self, body: dict, exchange: str, routing_key: str = ""):
        connection = EDAConnection.get_connection(self._connection_params)
        channel = connection.channel()

        message = amqp.Message(json.dumps(body).encode())

        channel.basic_publish(exchange=exchange, msg=message, routing_key=routing_key)
