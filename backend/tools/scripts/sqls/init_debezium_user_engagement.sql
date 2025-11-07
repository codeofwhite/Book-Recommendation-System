-- init_debezium_user_engagement.sql
-- 在 user_engagement_mysql_db 容器启动时执行此脚本

-- 创建 Debezium 用户并设置密码
-- 'debezium' 和 'dbz' 应该与 docker-compose.yml 中的 MYSQL_DEBEZIUM_USER 和 MYSQL_DEBEZIUM_PASSWORD 匹配
CREATE USER 'debezium'@'%' IDENTIFIED WITH mysql_native_password BY 'dbz';

-- 授予 Debezium 用户必要的权限
-- REPLICATION SLAVE 和 REPLICATION CLIENT 是 Debezium 捕获 binlog 所必需的
-- SELECT 权限是 Debezium 进行快照和读取表结构所必需的
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';

-- 如果您只想授予特定数据库的 SELECT 权限，可以这样写：
-- GRANT SELECT ON `book_engagement`.* TO 'debezium'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 验证用户和权限 (可选，用于调试)
-- SELECT user, host FROM mysql.user WHERE user = 'debezium';
-- SHOW GRANTS FOR 'debezium'@'%';
