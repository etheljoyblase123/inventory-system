-- DATABASE TEAM
-- Initial Data Seeder
-- Run this script after schema.sql to populate dummy data for testing.

USE inventory_system;

INSERT INTO products (name, category, price, stock, min_stock) VALUES
('Gaming Mouse', 'Electronics', 1200.00, 50, 10),
('Mechanical Keyboard', 'Electronics', 3500.00, 30, 5),
('Office Chair', 'Furniture', 4500.00, 15, 3),
('Gel Pen (Black)', 'Stationery', 15.00, 200, 50),
('A4 Printer Paper', 'Stationery', 250.00, 80, 20);

INSERT INTO stock_movements (product_id, type, quantity, reason) VALUES
(1, 'IN', 50, 'Initial Stock'),
(2, 'IN', 30, 'Initial Stock'),
(3, 'IN', 15, 'Initial Stock'),
(4, 'IN', 200, 'Initial Stock'),
(5, 'IN', 80, 'Initial Stock');
