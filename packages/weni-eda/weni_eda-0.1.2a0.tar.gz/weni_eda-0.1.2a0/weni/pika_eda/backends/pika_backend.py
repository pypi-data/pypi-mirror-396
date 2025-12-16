import time

import pika

from weni.pika_eda.connection_params import PikaConnectionParams
from weni.pika_eda import PikaConnection


class PikaConnectionBackend:  # pragma: no cover
    _start_message = "[+] Connection established. Waiting for events"

    def __init__(self, handle_consumers: callable):
        self._handle_consumers = handle_consumers

    def start_consuming(self, connection_params: PikaConnectionParams):
        connection = None
        while True:
            try:
                connection = PikaConnection.get_connection(connection_params)
                channel = connection.channel()

                self._handle_consumers(channel)

                print(self._start_message)

                channel.start_consuming()

            except (
                pika.exceptions.AMQPConnectionError,
                pika.exceptions.AMQPChannelError,
                ConnectionRefusedError,
                OSError,
            ) as error:
                print(f"[-] Connection error: {error}")
                print("    [+] Reconnecting in 5 seconds...")
                if connection and not connection.is_closed:
                    try:
                        connection.close()
                    except Exception:
                        pass
                PikaConnection.connection = None
                connection = None
                time.sleep(5)

            except KeyboardInterrupt:
                print("\n[+] Stopping consumer...")
                if connection and not connection.is_closed:
                    try:
                        connection.close()
                    except Exception:
                        pass
                break

            except Exception as error:
                # TODO: Handle exceptions with RabbitMQ
                print("error on start_consuming:", type(error), error)
                if connection and not connection.is_closed:
                    try:
                        connection.close()
                    except Exception:
                        pass
                PikaConnection.connection = None
                connection = None
                time.sleep(5)
