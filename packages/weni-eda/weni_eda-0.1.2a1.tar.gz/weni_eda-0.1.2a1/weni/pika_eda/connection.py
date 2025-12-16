import pika
from .connection_params import PikaConnectionParams


class PikaConnection:
    connection: pika.BlockingConnection = None

    @classmethod
    def get_connection(cls, connection_params: PikaConnectionParams) -> pika.BlockingConnection:
        if cls.connection is None or cls.connection.is_closed:
            connection_parameters = connection_params.get_connection_parameters()
            cls.connection = pika.BlockingConnection(connection_parameters)

        return cls.connection
