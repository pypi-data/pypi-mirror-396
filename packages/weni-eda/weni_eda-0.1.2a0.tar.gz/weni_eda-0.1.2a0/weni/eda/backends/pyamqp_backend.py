import time

import amqp

from weni.eda.connection_params import ConnectionParams
from weni.eda import EDAConnection


class PyAMQPConnectionBackend:  # pragma: no cover
    _start_message = "[+] Connection established. Waiting for events"

    def __init__(self, handle_consumers: callable):
        self._handle_consumers = handle_consumers

    def _drain_events(self, connection: amqp.connection.Connection):
        while True:
            connection.drain_events()

    def start_consuming(self, connection_params: ConnectionParams):
        while True:
            try:
                connection = EDAConnection.get_connection(connection_params)
                channel = connection.channel()

                self._handle_consumers(channel)

                print(self._start_message)

                self._drain_events(connection)

            except (
                amqp.exceptions.AMQPError,
                ConnectionRefusedError,
                OSError,
            ) as error:
                print(f"[-] Connection error: {error}")
                print("    [+] Reconnecting in 5 seconds...")
                time.sleep(5)

            except Exception as error:
                # TODO: Handle exceptions with RabbitMQ
                print("error on drain_events:", type(error), error)
                time.sleep(5)
