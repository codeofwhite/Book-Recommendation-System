-- init_debezium_user_engagement.sql
-- 在 user_engagement_mysql_db 容器启动时执行此脚本

-- 创建 Debezium 用户并设置密码
CREATE USER 'debezium'@'%' IDENTIFIED WITH mysql_native_password BY 'dbz';

-- 授予 Debezium 用户必要的权限
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';

-- 刷新权限
FLUSH PRIVILEGES;
