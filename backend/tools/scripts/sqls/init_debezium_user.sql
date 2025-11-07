-- backend/init_debezium_user.sql

-- 1. 创建 debezium 用户，密码设置为 'dbz'
--    IF NOT EXISTS 确保如果用户已经存在，不会报错
CREATE USER IF NOT EXISTS 'debezium'@'%' IDENTIFIED BY 'dbz';

-- 2. 赋予 debezium 用户所有权限（仅用于测试，排除所有权限问题）
--    在实际生产中，应只赋予所需权限，例如：
--    GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';
--    GRANT REFERENCES ON *.* TO 'debezium'@'%';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%';

-- 3. 刷新权限
FLUSH PRIVILEGES;