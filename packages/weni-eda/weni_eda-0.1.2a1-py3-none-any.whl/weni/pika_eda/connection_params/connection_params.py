from dataclasses import dataclass
from typing import Optional
import ssl

import pika


@dataclass
class PikaConnectionParams:
    host: str
    userid: str
    password: str
    port: int = 5672
    virtual_host: str = "/"
    ssl_options: Optional[pika.SSLOptions] = None

    @classmethod
    def create_ssl_options(
        cls,
        ca_certs: Optional[str] = None,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
        server_hostname: Optional[str] = None,
        host: Optional[str] = None,
    ) -> pika.SSLOptions:
        """
        Creates SSLOptions for pika connection with automatic SSL context creation.
        
        Args:
            ca_certs: Path to CA certificate file
            certfile: Path to client certificate file
            keyfile: Path to client key file
            server_hostname: Server hostname for SSL verification (required for security)
            host: Fallback hostname if server_hostname is not provided (defaults to connection host)
        
        Raises:
            ValueError: If neither server_hostname nor host is provided
        """
        context = ssl.create_default_context(cafile=ca_certs) if ca_certs else ssl.create_default_context()

        # Validate client certificate configuration: both certfile and keyfile must be provided together
        if certfile or keyfile:
            if not certfile:
                raise ValueError(
                    "PIKA_EDA_SSL_CERT_PATH must be provided when PIKA_EDA_SSL_KEY_PATH is set. "
                    "Both certificate and key files are required for client certificate authentication."
                )
            if not keyfile:
                raise ValueError(
                    "PIKA_EDA_SSL_KEY_PATH must be provided when PIKA_EDA_SSL_CERT_PATH is set. "
                    "Both certificate and key files are required for client certificate authentication."
                )
            context.load_cert_chain(certfile=certfile, keyfile=keyfile)

        # Security: server_hostname is required for proper SSL certificate verification
        # Use provided server_hostname, or fallback to host, or raise error
        if server_hostname:
            hostname = server_hostname
        elif host:
            hostname = host
        else:
            raise ValueError(
                "server_hostname or host must be provided for SSL connections "
                "to enable proper certificate verification and prevent MITM attacks"
            )

        return pika.SSLOptions(context, hostname)

    def get_connection_parameters(self) -> pika.ConnectionParameters:
        """
        Returns pika.ConnectionParameters configured with SSL if needed.
        """
        params = dict(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=pika.PlainCredentials(self.userid, self.password),
        )

        if self.ssl_options:
            params["ssl_options"] = self.ssl_options

        return pika.ConnectionParameters(**params)
