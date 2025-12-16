# Weni EDA

**weni-eda** is a Python library designed to simplify the use of Event-Driven Architecture (EDA). It provides an interface that seamlessly integrates with the Django framework and RabbitMQ messaging service. The design is scalable and intended to support various integrations in the future.

## Features
- Easy integration with Django.
- Support for RabbitMQ.
- Simplified event handling and message dispatching.
- Scalable design to accommodate future integrations with other frameworks and messaging services.
- **Two backends available**: `eda` (using amqp library) and `pika_eda` (using pika library with SSL support).
- **Automatic message acknowledgment**: Messages are automatically acknowledged when processing completes successfully.
- **Built-in JSON parsing**: Access parsed message body via `self.body` property with automatic caching.
- **Structured logging**: Built-in logger per consumer with contextual information.


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
    import amqp


    class ExampleConsumer(EDAConsumer):
        def consume(self, message: amqp.Message):
            # Access parsed body directly via self.body (automatically parsed and cached)
            data = self.body
            
            # Process your message
            user_id = data.get("user_id")
            action = data.get("action")
            
            # Log using the built-in logger
            self.logger.info(f"Processing action {action} for user {user_id}")
            
            # Message is automatically acknowledged if consume() completes without exception
            # You can also manually call self.ack() if needed
    ```

    **Key Features:**
    - `self.body`: Automatically parses and caches the JSON message body as a `dict`. No need to manually parse!
    - `self.logger`: Built-in logger instance (`eda.{ConsumerName}`) for structured logging.
    - `self.message_body`: Access the raw message body as bytes.
    - `self.delivery_tag`: Access the message delivery tag.
    - **Auto-ack**: Messages are automatically acknowledged when `consume()` completes successfully. If an exception is raised, the message is automatically rejected.
    - `self.ack()`: Manually acknowledge the message (usually not needed due to auto-ack).

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
    import pika


    class ExampleConsumer(PikaEDAConsumer):
        def consume(self, channel: pika.channel.Channel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes):
            # Access parsed body directly via self.body (automatically parsed and cached)
            data = self.body
            
            # Process your message
            user_id = data.get("user_id")
            action = data.get("action")
            
            # Log using the built-in logger
            self.logger.info(f"Processing action {action} for user {user_id}")
            
            # Message is automatically acknowledged if consume() completes without exception
            # You can also manually call self.ack() if needed
    ```

    **Key Features:**
    - `self.body`: Automatically parses and caches the JSON message body as a `dict`. No need to manually parse!
    - `self.logger`: Built-in logger instance (`pika_eda.{ConsumerName}`) for structured logging.
    - `self.message_body`: Access the raw message body as bytes.
    - `self.delivery_tag`: Access the message delivery tag.
    - **Auto-ack**: Messages are automatically acknowledged when `consume()` completes successfully. If an exception is raised, the message is automatically rejected.
    - `self.ack()`: Manually acknowledge the message (usually not needed due to auto-ack).

4. Registering your event handlers:  
    The `PIKA_EDA_CONSUMERS_HANDLE` variable indicates the function(s) that will be called when the consumer starts. This function will be responsible for mapping the messages to their respective consumers. The function must be declared as follows:
    ```py
    import pika

    from .example_consumer import ExampleConsumer


    def handle_consumers(channel: pika.channel.Channel):
        channel.basic_consume("example-queue", on_message_callback=ExampleConsumer().handle)
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

---

## Advanced Features

### Automatic Message Acknowledgment

By default, messages are automatically acknowledged when the `consume()` method completes successfully. If an exception is raised during processing, the message is automatically rejected (not requeued).

**Example:**
```py
class MyConsumer(EDAConsumer):
    def consume(self, message: amqp.Message):
        data = self.body
        # Process message...
        # If this completes without exception, message is auto-acknowledged
        # If an exception is raised, message is auto-rejected
```

To disable auto-ack for a specific consumer, you can set `_auto_ack_enabled = False` in your consumer class:
```py
class ManualAckConsumer(EDAConsumer):
    _auto_ack_enabled = False
    
    def consume(self, message: amqp.Message):
        # Process message...
        # Manually control when to ack
        if some_condition:
            self.ack()
```

### Structured Logging

Each consumer has a built-in logger that provides structured logging with contextual information:

```py
class MyConsumer(EDAConsumer):
    def consume(self, message: amqp.Message):
        # Use different log levels
        self.logger.debug("Debug information")
        self.logger.info("Processing message")
        self.logger.warning("Warning message")
        self.logger.error("Error occurred")
        
        # Logger name: eda.MyConsumer (or pika_eda.MyConsumer for PikaEDA)
```

When an exception occurs, the library automatically logs it with full context:
- Consumer name
- Error message
- Message body (decoded)
- Full stack trace

### Message Body Parsing

The `self.body` property automatically parses JSON messages and caches the result:

```py
class MyConsumer(EDAConsumer):
    def consume(self, message: amqp.Message):
        # First access parses and caches
        data = self.body  # Returns dict
        
        # Subsequent accesses use cached value (no re-parsing)
        user_id = self.body.get("user_id")
        action = self.body.get("action")
        
        # Access raw body if needed
        raw_body = self.message_body  # Returns bytes
```

### Error Handling

The library handles errors automatically:

```py
class MyConsumer(EDAConsumer):
    def consume(self, message: amqp.Message):
        # If an exception is raised here, the message is automatically:
        # 1. Rejected (not requeued)
        # 2. Logged with full context
        # 3. Exception is re-raised (you can catch it if needed)
        
        data = self.body
        if not data.get("required_field"):
            raise ValueError("Missing required field")  # Auto-rejected and logged
```

### Consumer Properties

Available properties on both `EDAConsumer` and `PikaEDAConsumer`:

- `self.body`: Parsed message body as `dict` (cached)
- `self.message_body`: Raw message body as `bytes`
- `self.delivery_tag`: Message delivery tag
- `self.logger`: Logger instance for structured logging
- `self.ack()`: Manually acknowledge the message
