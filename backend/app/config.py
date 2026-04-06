from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "K8s Health Check"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security - SECRET_KEY must be set in production
    SECRET_KEY: str
    ALLOWED_ORIGINS: str = ""  # Comma-separated list of allowed CORS origins

    @classmethod
    def model_validate(cls, obj):
        # Generate a warning if SECRET_KEY is not set (development only)
        if not obj.get("SECRET_KEY"):
            import warnings
            warnings.warn(
                "SECRET_KEY not set. A temporary key will be generated. "
                "This is NOT secure for production. Set SECRET_KEY in your .env file.",
                UserWarning
            )
            obj["SECRET_KEY"] = secrets.token_urlsafe(32)
        return super().model_validate(obj)

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
