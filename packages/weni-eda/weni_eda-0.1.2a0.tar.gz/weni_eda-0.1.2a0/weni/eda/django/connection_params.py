from django.conf import settings

from weni.eda.connection_params import ConnectionParams, ParamsFactory


class ConnectionParamsFactory(ParamsFactory):

    @classmethod
    def get_params(cls) -> ConnectionParams:
        return ConnectionParams(
            host=settings.EDA_BROKER_HOST,
            port=settings.EDA_BROKER_PORT,
            userid=settings.EDA_BROKER_USER,
            password=settings.EDA_BROKER_PASSWORD,
            virtual_host=settings.EDA_VIRTUAL_HOST,
        )
