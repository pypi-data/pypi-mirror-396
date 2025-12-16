import amqp
from .connection_params import ConnectionParams


class EDAConnection:
    connection: amqp.Connection = None

    @classmethod
    def get_connection(cls, connection_params: ConnectionParams) -> amqp.Connection:
        if cls.connection is None or not cls.connection.connected:
            cls.connection = amqp.Connection(**connection_params.value)
            cls.connection.connect()

        return cls.connection
