from sanic_envconfig import EnvConfig


class MainSettings(EnvConfig):
    DEBUG: bool = True
    HOST: str = '0.0.0.0' # Use localhost instead of 0.0.0.0
    PORT: int = 8080
    DB_URL: str = ''
