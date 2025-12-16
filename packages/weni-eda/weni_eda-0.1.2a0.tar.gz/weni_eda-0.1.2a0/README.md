# Weni EDA

**weni-eda** is a Python library designed to simplify the use of Event-Driven Architecture (EDA). It provides an interface that seamlessly integrates with the Django framework and RabbitMQ messaging service. The design is scalable and intended to support various integrations in the future.

## Features
- Easy integration with Django.
- Support for RabbitMQ.
- Simplified event handling and message dispatching.
- Scalable design to accommodate future integrations with other frameworks and messaging services.
- **Two backends available**: `eda` (using amqp library) and `pika_eda` (using pika library with SSL support).


## Installation
To install the library, use pip:

```
pip install weni-eda
```

## Configuration
### Django Integration

1. Add weni-eda to your Django project:  
Add `weni.eda.django.eda_app` to your `INSTALLED_APPS` in `settings.py`:
    ```py
    # settings.py
    INSTALLED_APPS = [
        # ... other installed apps
        'weni.eda.django.eda_app',
    ]
    ```

2. Environment Variables for weni-eda Configuration

    The following environment variables are used to configure the weni-eda library. Here is a detailed explanation of each variable:

    | Variable Name          | Examples                                     | Description                                                     |
    |------------------------|----------------------------------------------|-----------------------------------------------------------------|
    | `EDA_CONSUMERS_HANDLE` | `"example.event_driven.handle.handle_consumers"` | Specifies the handler module for consumer events.               |
    | `EDA_BROKER_HOST`      | `"localhost"`                                | The hostname or IP address of the message broker server.        |
    | `EDA_VIRTUAL_HOST`     | `"/"`                                        | The virtual host to use when connecting to the broker.          |
    | `EDA_BROKER_PORT`      | `5672`                                       | The port number on which the message broker is listening.       |
    | `EDA_BROKER_USER`      | `"guest"`                                    | The username for authenticating with the message broker.        |
    | `EDA_BROKER_PASSWORD`  | `"guest"`                                    | The password for authenticating with the message broker.        |

3. Creating your event consumers  
    We provide an abstract class that facilitates the consumption of messages. To use it, you need to inherit it and declare the `consume` method as follows:
    ```py
    from weni.eda.django.consumers import EDAConsumer


    class ExampleConsumer(EDAConsumer):
        def consume(self, message: Message):
            body = JSONParser.parse(message.body)
            self.ack()
    ```

    - `JSONParser.parse(message.body)` Converts the message arriving from RabbitMQ in JSON format to `dict`
    - `self.ack()` Confirms to RabbitMQ that the message can be removed from the queue, which prevents it from being reprocessed.

4. Registering your event handlers:  
    the `EDA_CONSUMERS_HANDLE` variable indicates the function that will be called when the consumer starts. this function will be responsible for mapping the messages to their respective consumers. The function must be declared as follows:
    ```py
    import amqp

    from .example_consumer import ExampleConsumer


    def handle_consumers(channel: amqp.Channel):
        channel.basic_consume("example-queue", callback=ExampleConsumer().handle)
    ```
    This indicates that any message arriving at the `example-queue` queue will be dispatched to the `ExampleConsumer` consumer and will fall into its `consume` method.

5. Starting to consume the queues  
    To start consuming messages from the queue, you need to run the `edaconsume` command as follows:
    ```sh
    python manage.py edaconsume
    ```

    From then on, all messages that arrive in the queues where your application is written will be dispatched to their respective consumers.

---

## Pika EDA (SSL Support)

**pika_eda** is an alternative backend that uses the `pika` library instead of `amqp`. It provides the same functionality as `eda` but with additional features:

- **SSL/TLS support**: Secure connections with automatic SSL certificate verification
- **Multiple handles**: Support for multiple consumer handlers in a single application
- **Enhanced security**: Proper hostname verification to prevent MITM attacks

### Configuration

1. Add pika_eda to your Django project:  
Add `weni.pika_eda.django.pika_eda_app` to your `INSTALLED_APPS` in `settings.py`:
    ```py
    # settings.py
    INSTALLED_APPS = [
        # ... other installed apps
        'weni.pika_eda.django.pika_eda_app',
    ]
    ```

2. Environment Variables for pika_eda Configuration

    The following environment variables are used to configure the pika_eda library:

    | Variable Name                    | Examples                                     | Description                                                     |
    |-----------------------------------|----------------------------------------------|-----------------------------------------------------------------|
    | `PIKA_EDA_CONSUMERS_HANDLE`       | `"example.event_driven.handle.handle_consumers"` or `["handle1", "handle2"]` | Specifies the handler module(s) for consumer events. Can be a string or a list of strings for multiple handles. |
    | `PIKA_EDA_BROKER_HOST`            | `"localhost"`                                | The hostname or IP address of the message broker server.        |
    | `PIKA_EDA_VIRTUAL_HOST`           | `"/"`                                        | The virtual host to use when connecting to the broker.          |
    | `PIKA_EDA_BROKER_PORT`            | `5671` (SSL) or `5672` (non-SSL)            | The port number on which the message broker is listening.       |
    | `PIKA_EDA_BROKER_USER`            | `"guest"`                                    | The username for authenticating with the message broker.        |
    | `PIKA_EDA_BROKER_PASSWORD`        | `"guest"`                                    | The password for authenticating with the message broker.        |
    | `PIKA_EDA_SSL_ENABLED`            | `True`                                       | Enable SSL/TLS connections (optional).                          |
    | `PIKA_EDA_SSL_CERT_PATH`           | `"/path/to/cert.pem"`                       | Path to client certificate file (optional, for mutual auth).    |
    | `PIKA_EDA_SSL_KEY_PATH`            | `"/path/to/key.pem"`                        | Path to client private key file (optional, for mutual auth).    |
    | `PIKA_EDA_SSL_CA_CERTS`            | `"/path/to/ca.pem"`                         | Path to CA certificate file (optional).                         |
    | `PIKA_EDA_SSL_SERVER_HOSTNAME`     | `"rabbitmq.example.com"`                    | Server hostname for SSL verification (optional, defaults to PIKA_EDA_BROKER_HOST). |

3. Creating your event consumers  
    We provide an abstract class that facilitates the consumption of messages. To use it, you need to inherit it and declare the `consume` method as follows:
    ```py
    from weni.pika_eda.django.consumers import PikaEDAConsumer
    from weni.pika_eda.parsers import JSONParser

    import pika


    class ExampleConsumer(PikaEDAConsumer):
        def consume(self, channel: pika.channel.Channel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes):
            body_dict = JSONParser.parse(body)
            self.ack()
    ```

    - `JSONParser.parse(body)` Converts the message body from RabbitMQ in JSON format to `dict`
    - `self.ack()` Confirms to RabbitMQ that the message can be removed from the queue, which prevents it from being reprocessed.

4. Registering your event handlers:  
    The `PIKA_EDA_CONSUMERS_HANDLE` variable indicates the function(s) that will be called when the consumer starts. This function will be responsible for mapping the messages to their respective consumers. The function must be declared as follows:
    ```py
    import pika

    from .example_consumer import ExampleConsumer


    def handle_consumers(channel: pika.channel.Channel):
        channel.basic_consume("example-queue", callback=ExampleConsumer().handle)
    ```
    This indicates that any message arriving at the `example-queue` queue will be dispatched to the `ExampleConsumer` consumer and will fall into its `consume` method.

    **Multiple Handles**: If you need multiple consumer handlers, you can set `PIKA_EDA_CONSUMERS_HANDLE` as a list:
    ```py
    # settings.py
    PIKA_EDA_CONSUMERS_HANDLE = [
        "app1.handlers.handle_consumers",
        "app2.handlers.handle_consumers",
    ]
    ```
    Then specify which handle to use when running the command:
    ```sh
    python manage.py pikaconsume --handle-index 0  # Uses first handle
    python manage.py pikaconsume --handle-index 1  # Uses second handle
    ```

5. Starting to consume the queues  
    To start consuming messages from the queue, you need to run the `pikaconsume` command as follows:
    ```sh
    python manage.py pikaconsume
    ```
    
    If using multiple handles, specify the handle index:
    ```sh
    python manage.py pikaconsume --handle-index 0
    ```

    From then on, all messages that arrive in the queues where your application is written will be dispatched to their respective consumers.

### SSL Configuration Example

For secure connections with SSL:
```py
# settings.py
PIKA_EDA_BROKER_HOST = "rabbitmq.example.com"
PIKA_EDA_BROKER_PORT = 5671  # SSL port
PIKA_EDA_BROKER_USER = "myuser"
PIKA_EDA_BROKER_PASSWORD = "mypassword"
PIKA_EDA_SSL_ENABLED = True
PIKA_EDA_SSL_CA_CERTS = "/path/to/ca_certificate.pem"
PIKA_EDA_SSL_SERVER_HOSTNAME = "rabbitmq.example.com"  # Optional, defaults to PIKA_EDA_BROKER_HOST
```

**Security Note**: The library automatically uses the broker hostname for SSL verification if `PIKA_EDA_SSL_SERVER_HOSTNAME` is not explicitly set, ensuring proper certificate verification and preventing MITM attacks.
