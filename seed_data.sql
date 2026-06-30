-- seed_data.sql
-- Sample data for testing the Restaurant POS UI.
-- Run this in pgAdmin's Query Tool against your project database.

-- Clear existing data (keeps table structure, resets IDs)
TRUNCATE TABLE order_items, orders, restaurant_tables, employees, customers, menu_items
RESTART IDENTITY CASCADE;

-- =========================
-- MENU ITEMS
-- =========================
INSERT INTO menu_items (name, category, price, stock) VALUES
('Margherita Pizza', 'Pizza', 12.50, 25),
('Pepperoni Pizza', 'Pizza', 14.00, 20),
('Spaghetti Carbonara', 'Pasta', 13.75, 18),
('Fettuccine Alfredo', 'Pasta', 13.25, 15),
('Caesar Salad', 'Salad', 8.50, 30),
('Greek Salad', 'Salad', 8.00, 22),
('Grilled Chicken Burger', 'Burger', 11.00, 20),
('Classic Cheeseburger', 'Burger', 10.50, 4),
('French Fries', 'Sides', 4.50, 50),
('Garlic Bread', 'Sides', 5.00, 3),
('Tiramisu', 'Dessert', 6.50, 12),
('Chocolate Lava Cake', 'Dessert', 7.00, 10),
('Coca-Cola', 'Beverage', 2.50, 60),
('Iced Tea', 'Beverage', 2.50, 40),
('Espresso', 'Beverage', 3.00, 35);

-- =========================
-- CUSTOMERS
-- =========================
INSERT INTO customers (name, phone) VALUES
('Olivia Bennett', '0412345678'),
('Liam Carter', '0423456789'),
('Emma Davidson', '0434567890'),
('Noah Fletcher', '0445678901'),
('Ava Grayson', '0456789012'),
('William Harper', '0467890123'),
('Sophia Iverson', '0478901234'),
('James Kingston', '0489012345');

-- =========================
-- EMPLOYEES
-- =========================
INSERT INTO employees (name, role, salary) VALUES
('Daniel Brooks', 'Manager', 65000),
('Maria Lopez', 'Chef', 52000),
('Ethan Walsh', 'Chef', 48000),
('Grace Nolan', 'Waiter', 38000),
('Lucas Reid', 'Waiter', 37500),
('Chloe Adams', 'Cashier', 40000);

-- =========================
-- RESTAURANT TABLES
-- =========================
INSERT INTO restaurant_tables (capacity, status) VALUES
(2, 'Available'),
(2, 'Available'),
(4, 'Available'),
(4, 'Occupied'),
(6, 'Available'),
(6, 'Reserved'),
(8, 'Available');

-- =========================
-- ORDERS + ORDER ITEMS
-- (order totals are computed to match the items inserted below)
-- =========================

-- Order 1: Olivia, Table 4, Completed, placed 2 days ago
-- Items: Margherita 12.50 + Fries x2 9.00 + Coca-Cola x2 5.00 + Tiramisu 6.50 = 33.00
INSERT INTO orders (customer_id, table_id, status, total, order_date) VALUES
(1, 4, 'Completed', 33.00, CURRENT_DATE - INTERVAL '2 days');

INSERT INTO order_items (order_id, item_id, quantity, subtotal) VALUES
(1, 1, 1, 12.50),   -- Margherita Pizza
(1, 9, 2, 9.00),    -- French Fries x2
(1, 13, 2, 5.00),   -- Coca-Cola x2
(1, 11, 1, 6.50);   -- Tiramisu

-- Order 2: Liam, Table 3, Active, placed today
-- Items: Burger 11.00 + Caesar Salad 8.50 + Iced Tea x2 5.00 + Coca-Cola 2.50 = 27.00
INSERT INTO orders (customer_id, table_id, status, total, order_date) VALUES
(2, 3, 'Active', 27.00, CURRENT_DATE);

INSERT INTO order_items (order_id, item_id, quantity, subtotal) VALUES
(2, 7, 1, 11.00),   -- Grilled Chicken Burger
(2, 5, 1, 8.50),    -- Caesar Salad
(2, 14, 2, 5.00),   -- Iced Tea x2
(2, 13, 1, 2.50);   -- Coca-Cola

-- Order 3: Emma, Table 6, Active, placed today
-- Items: Pepperoni Pizza x2 28.00 + Garlic Bread 5.00 + Lava Cake 7.00 + Coca-Cola 2.50 = 42.50
INSERT INTO orders (customer_id, table_id, status, total, order_date) VALUES
(3, 6, 'Active', 42.50, CURRENT_DATE);

INSERT INTO order_items (order_id, item_id, quantity, subtotal) VALUES
(3, 2, 2, 28.00),   -- Pepperoni Pizza x2
(3, 10, 1, 5.00),   -- Garlic Bread
(3, 12, 1, 7.00),   -- Chocolate Lava Cake
(3, 13, 1, 2.50);   -- Coca-Cola

-- Order 4: Noah, Table 4, Completed, placed yesterday
-- Items: Carbonara 13.75 + Fries 4.50 + Espresso 3.00 + Iced Tea 2.50 = 23.75
INSERT INTO orders (customer_id, table_id, status, total, order_date) VALUES
(4, 4, 'Completed', 23.75, CURRENT_DATE - INTERVAL '1 day');

INSERT INTO order_items (order_id, item_id, quantity, subtotal) VALUES
(4, 3, 1, 13.75),   -- Spaghetti Carbonara
(4, 9, 1, 4.50),    -- French Fries
(4, 15, 1, 3.00),   -- Espresso
(4, 14, 1, 2.50);   -- Iced Tea

-- Order 5: Ava, Table 2, Completed, placed 10 days ago (for monthly chart variety)
-- Items: Cheeseburger 10.50 + Fries 4.50 + Coca-Cola 2.50 + Iced Tea 2.50 = 20.00
INSERT INTO orders (customer_id, table_id, status, total, order_date) VALUES
(5, 2, 'Completed', 20.00, CURRENT_DATE - INTERVAL '10 days');

INSERT INTO order_items (order_id, item_id, quantity, subtotal) VALUES
(5, 8, 1, 10.50),   -- Classic Cheeseburger
(5, 9, 1, 4.50),    -- French Fries
(5, 13, 1, 2.50),   -- Coca-Cola
(5, 14, 1, 2.50);   -- Iced Tea

-- Order 6: William, Table 1, Active, placed today (small order)
INSERT INTO orders (customer_id, table_id, status, total, order_date) VALUES
(6, 1, 'Active', 11.00, CURRENT_DATE);

INSERT INTO order_items (order_id, item_id, quantity, subtotal) VALUES
(6, 7, 1, 11.00);   -- Grilled Chicken Burger

-- Mark table 4 and table 6 occupied to match the "Active" orders above
UPDATE restaurant_tables SET status = 'Occupied' WHERE table_id IN (3, 6, 1);

-- =========================
-- VERIFY
-- =========================
SELECT 'menu_items' AS table_name, COUNT(*) FROM menu_items
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'employees', COUNT(*) FROM employees
UNION ALL SELECT 'restaurant_tables', COUNT(*) FROM restaurant_tables
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items;
