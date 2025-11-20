-- 1. 创建 debezium 用户，密码设置为 'dbz'
CREATE USER IF NOT EXISTS 'debezium'@'%' IDENTIFIED BY 'dbz';

-- 2. 赋予 debezium 用户所有权限（仅用于测试，排除所有权限问题）
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';

-- 3. 刷新权限
FLUSH PRIVILEGES;