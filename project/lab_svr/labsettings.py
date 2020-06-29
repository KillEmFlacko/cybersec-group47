from sanic_envconfig import EnvConfig


class LabSettings(EnvConfig):
    DEBUG: bool = True
    HOST: str = '0.0.0.0' # Use localhost instead of 0.0.0.0
    PORT: int = 8000
    DB_URL: str = ''
