from pydantic_settings import BaseSettings
from typing import Optional
import secrets
import warnings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "K8s Health Check"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security - SECRET_KEY with auto-generate for missing
    SECRET_KEY: str = ""
    ALLOWED_ORIGINS: str = ""  # Comma-separated list of allowed CORS origins

    def __init__(self, **kwargs):
        # Check if SECRET_KEY is set
        import os
        env_secret = os.getenv("SECRET_KEY", "")
        if not env_secret and not kwargs.get("SECRET_KEY"):
            warnings.warn(
                "SECRET_KEY not set. A temporary key will be generated. "
                "This is NOT secure for production. Set SECRET_KEY in your .env file "
                "or as environment variable.",
                UserWarning
            )
            if not kwargs.get("SECRET_KEY"):
                kwargs["SECRET_KEY"] = secrets.token_urlsafe(32)
        elif env_secret and not kwargs.get("SECRET_KEY"):
            kwargs["SECRET_KEY"] = env_secret
        super().__init__(**kwargs)

    # Kubernetes
    K8S_APISERVER_URL: str = "https://kubernetes.default.svc"
    K8S_TOKEN_PATH: str = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    K8S_SSL_VERIFY: bool = True

    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "k8s_monitor"
    MYSQL_PASSWORD: str = "changeme"
    MYSQL_DATABASE: str = "k8s_monitor"
    MYSQL_POOL_SIZE: int = 10

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_CACHE_TTL: int = 30  # seconds

    # Collector
    COLLECTOR_INTERVAL: int = 15  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
