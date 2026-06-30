CREATE TABLE menu_items (
    item_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    price NUMERIC(10,2),
    stock INTEGER
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20)
);

CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(50),
    salary NUMERIC(10,2)
);

CREATE TABLE restaurant_tables (
    table_id SERIAL PRIMARY KEY,
    capacity INTEGER,
    status VARCHAR(20)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    table_id INTEGER REFERENCES restaurant_tables(table_id),
    status VARCHAR(20),
    total NUMERIC(10,2),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    item_id INTEGER REFERENCES menu_items(item_id),
    quantity INTEGER,
    subtotal NUMERIC(10,2)
);

