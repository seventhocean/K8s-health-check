-- Initialize database for K8s Monitor
-- This script runs when MySQL container starts for the first time

CREATE DATABASE IF NOT EXISTS k8s_monitor;
USE k8s_monitor;

-- Grant privileges
GRANT ALL PRIVILEGES ON k8s_monitor.* TO 'k8s_monitor'@'%' IDENTIFIED BY 'changeme';
FLUSH PRIVILEGES;
