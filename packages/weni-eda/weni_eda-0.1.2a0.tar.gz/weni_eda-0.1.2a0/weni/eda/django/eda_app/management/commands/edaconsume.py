from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from weni.eda.backends.pyamqp_backend import PyAMQPConnectionBackend
from weni.eda.django.connection_params import ConnectionParamsFactory


handle_consumers_function = import_string(settings.EDA_CONSUMERS_HANDLE)


def get_connection_backend():  # pragma: no cover
    if hasattr(settings, "EDA_CONNECTION_BACKEND"):
        return import_string(settings.EDA_CONNECTION_BACKEND)(handle_consumers_function)

    return PyAMQPConnectionBackend(handle_consumers_function)


class Command(BaseCommand):  # pragma: no cover
    def handle(self, *args, **options):
        connection_params = ConnectionParamsFactory.get_params()
        get_connection_backend().start_consuming(connection_params)
