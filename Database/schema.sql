-- DATABASE TEAM
-- Inventory System Database Schema
-- Run this script to generate the database structure.

CREATE DATABASE IF NOT EXISTS inventory_system;
USE inventory_system;

-- 1. Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    category   VARCHAR(50),
    price      DECIMAL(10,2) NOT NULL,
    stock      INT DEFAULT 0,
    min_stock  INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Sales Table
CREATE TABLE IF NOT EXISTS sales (
    sale_id      INT AUTO_INCREMENT PRIMARY KEY,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Sale Items Table
CREATE TABLE IF NOT EXISTS sale_items (
    sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id      INT NOT NULL,
    product_id   INT NOT NULL,
    quantity     INT NOT NULL,
    price        DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (sale_id)    REFERENCES sales(sale_id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

-- 4. Stock Movements Log Table
CREATE TABLE IF NOT EXISTS stock_movements (
    movement_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id  INT NOT NULL,
    type        ENUM('IN','OUT') NOT NULL,
    quantity    INT NOT NULL,
    reason      VARCHAR(100),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);
