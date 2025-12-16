from django.conf import settings

from weni.pika_eda.connection_params import PikaConnectionParams, PikaParamsFactory


class PikaConnectionParamsFactory(PikaParamsFactory):

    @classmethod
    def get_params(cls) -> PikaConnectionParams:
        ssl_options = None

        # Automatic SSL detection: if SSL is enabled or SSL cert path is set
        ssl_enabled = getattr(settings, "PIKA_EDA_SSL_ENABLED", False)
        ssl_cert_path = getattr(settings, "PIKA_EDA_SSL_CERT_PATH", None)
        ssl_key_path = getattr(settings, "PIKA_EDA_SSL_KEY_PATH", None)
        ssl_ca_certs = getattr(settings, "PIKA_EDA_SSL_CA_CERTS", None)
        ssl_server_hostname = getattr(settings, "PIKA_EDA_SSL_SERVER_HOSTNAME", None)

        if ssl_enabled or ssl_cert_path or ssl_ca_certs:
            # Get host for fallback if server_hostname is not explicitly set
            host = settings.PIKA_EDA_BROKER_HOST
            ssl_options = PikaConnectionParams.create_ssl_options(
                ca_certs=ssl_ca_certs,
                certfile=ssl_cert_path,
                keyfile=ssl_key_path,
                server_hostname=ssl_server_hostname,
                host=host,  # Use connection host as fallback for SSL verification
            )

        # Use SSL port (5671) if SSL is enabled, otherwise use regular port (5672)
        port = getattr(settings, "PIKA_EDA_BROKER_PORT", 5671 if ssl_options else 5672)

        return PikaConnectionParams(
            host=settings.PIKA_EDA_BROKER_HOST,
            port=port,
            userid=settings.PIKA_EDA_BROKER_USER,
            password=settings.PIKA_EDA_BROKER_PASSWORD,
            virtual_host=getattr(settings, "PIKA_EDA_VIRTUAL_HOST", "/"),
            ssl_options=ssl_options,
        )
