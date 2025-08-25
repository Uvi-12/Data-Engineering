CREATE DATABASE retail

CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE payment_methods (
    id INT PRIMARY KEY AUTO_INCREMENT,
    method_name VARCHAR(100) NOT NULL
);

CREATE TABLE sales_channels (
    id INT PRIMARY KEY AUTO_INCREMENT,
    channel_name VARCHAR(100) NOT NULL
);

CREATE TABLE sales (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE sale_line_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO customers (name) VALUES
('Kapil'),
('Yuvraj'),
('Om');

INSERT INTO products (name, base_price) VALUES
('Pen', 10.00),
('Notebook', 50.00);

INSERT INTO sales (customer_id) VALUES
(1),
(2);

INSERT INTO sale_line_items (sale_id, product_id, quantity, unit_price) VALUES
(1, 1, 5, 10.00),
(1, 2, 1, 50.00),
(2, 1, 3, 10.00);

SELECT * FROM customers;

SELECT * FROM products;

-- Kapil bought
SELECT
    c.name,
    p.name AS product_name,
    sli.quantity,
    sli.unit_price
FROM
    customers c
JOIN
    sales s ON c.id = s.customer_id
JOIN
    sale_line_items sli ON s.id = sli.sale_id
JOIN
    products p ON sli.product_id = p.id
WHERE
    c.name = 'Kapil';

-- revenue
SELECT SUM(quantity * unit_price) AS total_revenue
FROM sale_line_items;

-- sales
SELECT
    c.name,
    SUM(sli.quantity * sli.unit_price) AS customer_total
FROM
    customers c
JOIN
    sales s ON c.id = s.customer_id
JOIN
    sale_line_items sli ON s.id = sli.sale_id
GROUP BY
    c.name;
