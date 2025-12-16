import json

from .connection_params import PikaParamsFactory
from .connection import PikaConnection


class PikaEDAPublisher:
    def __init__(self, connection_params_factory: PikaParamsFactory):
        self._connection_params = connection_params_factory.get_params()

    def send_message(self, body: dict, exchange: str, routing_key: str = ""):
        connection = PikaConnection.get_connection(self._connection_params)
        channel = connection.channel()

        try:
            message_body = json.dumps(body).encode()

            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message_body,
            )
        finally:
            if channel and not channel.is_closed:
                channel.close()
