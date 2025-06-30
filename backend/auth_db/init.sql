-- auth_db/init.sql
-- 创建 Debezium 用户并授予复制权限
CREATE USER 'debezium'@'%' IDENTIFIED WITH mysql_native_password BY 'dbz';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';
-- 对于 MySQL 8.0+, 需要额外的 'binlog monitor' 权限
GRANT BINLOG MONITOR ON *.* TO 'debezium'@'%';
-- 如果你需要允许 Debezium 执行 DDL 语句 (不推荐在生产环境)
-- GRANT CREATE, ALTER, DROP, REFERENCES ON auth_db.* TO 'debezium'@'%';
FLUSH PRIVILEGES;

-- 确保 'auth_db' 存在且 Debezium 用户有权限访问它
CREATE DATABASE IF NOT EXISTS auth_db;
USE auth_db;
-- 创建或修改你的 users 表，确保它有一个主键
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL
);
-- 插入一些测试数据（可选）
INSERT INTO users (username, email, password_hash) VALUES ('testuser_debezium', 'debezium@test.com', 'test_hash_123') ON DUPLICATE KEY UPDATE username=username;