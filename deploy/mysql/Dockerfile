# Custom MySQL image with initialization scripts
FROM registry.aliyuncs.com/library/mysql:8.0

# Copy initialization scripts
COPY deploy/mysql/init.sql /docker-entrypoint-initdb.d/init.sql

# Optional: Set default environment variables
ENV MYSQL_ROOT_PASSWORD=rootpassword
ENV MYSQL_DATABASE=k8s_monitor
ENV MYSQL_USER=k8s_monitor
ENV MYSQL_PASSWORD=changeme
