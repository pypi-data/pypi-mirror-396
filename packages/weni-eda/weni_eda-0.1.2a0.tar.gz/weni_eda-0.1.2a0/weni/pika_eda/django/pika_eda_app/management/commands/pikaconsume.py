from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from weni.pika_eda.backends.pika_backend import PikaConnectionBackend
from weni.pika_eda.django.connection_params import PikaConnectionParamsFactory


def get_handle_consumers_function(handle_index: int = None):
    """
    Gets the handle_consumers function from settings.
    Supports both single string and list of strings for PIKA_EDA_CONSUMERS_HANDLE.
    """
    consumers_handle = getattr(settings, "PIKA_EDA_CONSUMERS_HANDLE", None)

    if consumers_handle is None:
        raise ValueError("PIKA_EDA_CONSUMERS_HANDLE must be set in settings")

    if isinstance(consumers_handle, list):
        if handle_index is None:
            raise ValueError(
                "PIKA_EDA_CONSUMERS_HANDLE is a list. Please specify --handle-index to select which handle to use."
            )
        if handle_index >= len(consumers_handle):
            raise ValueError(
                f"handle-index {handle_index} is out of range. Available handles: 0-{len(consumers_handle) - 1}"
            )
        handle_path = consumers_handle[handle_index]
    else:
        handle_path = consumers_handle

    return import_string(handle_path)


def get_connection_backend(handle_consumers_function):  # pragma: no cover
    if hasattr(settings, "PIKA_EDA_CONNECTION_BACKEND"):
        return import_string(settings.PIKA_EDA_CONNECTION_BACKEND)(handle_consumers_function)

    return PikaConnectionBackend(handle_consumers_function)


class Command(BaseCommand):  # pragma: no cover
    help = "Start consuming messages from RabbitMQ using pika"

    def add_arguments(self, parser):
        parser.add_argument(
            "--handle-index",
            type=int,
            default=None,
            help="Index of the handle to use when PIKA_EDA_CONSUMERS_HANDLE is a list",
        )

    def handle(self, *args, **options):
        handle_index = options.get("handle_index")
        handle_consumers_function = get_handle_consumers_function(handle_index)
        connection_params = PikaConnectionParamsFactory.get_params()
        get_connection_backend(handle_consumers_function).start_consuming(connection_params)
