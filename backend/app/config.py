from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "K8s Health Check"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

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
