# Custom MySQL image with initialization scripts
FROM mysql:8.0

# 使用国内镜像源 (MySQL 官方镜像已经较小，一般不需要替换)
# COPY deploy/mysql/init.sql /docker-entrypoint-initdb.d/init.sql

# Copy initialization scripts
COPY deploy/mysql/init.sql /docker-entrypoint-initdb.d/init.sql

# Optional: Set default environment variables
ENV MYSQL_ROOT_PASSWORD=rootpassword
ENV MYSQL_DATABASE=k8s_monitor
ENV MYSQL_USER=k8s_monitor
ENV MYSQL_PASSWORD=changeme
