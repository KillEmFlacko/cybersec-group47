from sanic_envconfig import EnvConfig


class Settings(EnvConfig):
    DEBUG: bool = True
    HOST: str = '0.0.0.0' # Use localhost instead of 0.0.0.0
    PORT: int = 8080
    DB_URL: str = ''
    DAY_PARTS: int = 0
    CERT: str = ''
    KEY: str = ''
    DATE_FORMAT: str = ''
    CA_DIR: str = ''
