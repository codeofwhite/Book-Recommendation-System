-- backend/init_recommendation_db.sql

-- Ensure the database exists (it should be created by MYSQL_DATABASE env var, but doesn't hurt)
CREATE DATABASE IF NOT EXISTS recommendation_db;
USE recommendation_db;

-- Create the rec_user_profiles table
-- 根据 auth_db.users 表的实际结构进行调整
CREATE TABLE IF NOT EXISTS rec_user_profiles (
    id INT PRIMARY KEY,                       -- 匹配 auth_db.users 的 id
    username VARCHAR(80) UNIQUE NOT NULL,     -- 匹配 auth_db.users 的 username
    email VARCHAR(120) UNIQUE NOT NULL,       -- 匹配 auth_db.users 的 email
    password_hash VARCHAR(128) NOT NULL,      -- 匹配 auth_db.users 的 password_hash
    avatar_url VARCHAR(255),                  -- 匹配 auth_db.users 的 avatar_url (可空)
    last_sync_time DATETIME                   -- 用于记录同步时间，可选，但建议保留
);

-- Add other tables for recommendation_db here if needed, e.g.:
-- CREATE TABLE IF NOT EXISTS recommendations (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     user_id INT, -- 注意这里如果 user_id 是 INT 类型
--     book_id VARCHAR(255),
--     score DECIMAL(5,2),
--     FOREIGN KEY (user_id) REFERENCES rec_user_profiles(id) -- 注意这里引用的是 rec_user_profiles 的 id
-- );