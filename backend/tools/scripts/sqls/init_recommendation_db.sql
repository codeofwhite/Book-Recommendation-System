-- backend/init_recommendation_db.sql

-- Ensure the database exists (it should be created by MYSQL_DATABASE env var, but doesn't hurt)
CREATE DATABASE IF NOT EXISTS recommendation_db;
USE recommendation_db;

-- Create the rec_user_profiles table
CREATE TABLE IF NOT EXISTS rec_user_profiles (
    id INT PRIMARY KEY,                       
    username VARCHAR(80) UNIQUE NOT NULL,     
    email VARCHAR(120) UNIQUE NOT NULL,       
    password_hash VARCHAR(128) NOT NULL,      
    avatar_url VARCHAR(255),                  
    last_sync_time DATETIME                   
);
