-- 데이터베이스 권한 설정 및 부여
Drop database handwritten_db;

USE mysql;

CREATE DATABASE handwritten_db;

CREATE USER 'capstone'@'localhost' IDENTIFIED BY 'capstone';

CREATE USER 'capstone'@'%' IDENTIFIED BY 'capstone';


-- 권한 부여

GRANT ALL PRIVILEGES ON handwritten_db.* TO 'capstone'@'localhost';

GRANT ALL PRIVILEGES ON handwritten_db.* TO 'capstone'@'%';

FLUSH PRIVILEGES;


-- 테이블 설정 및 데티어 삽입 
USE handwritten_db;

CREATE TABLE User(
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    passwd VARCHAR(256),
    nickname VARCHAR(31)
);

INSERT INTO User(email, passwd, nickname) VALUES ('', '', '');

SELECT * FROM User;
