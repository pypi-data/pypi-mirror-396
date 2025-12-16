from dataclasses import dataclass


@dataclass
class ConnectionParams:
    host: str
    userid: str
    password: str
    port: str = "5421"
    virtual_host: str = "/"

    @property
    def value(self):
        return dict(
            host=self.host,
            port=self.port,
            userid=self.userid,
            password=self.password,
            virtual_host=self.virtual_host,
        )
