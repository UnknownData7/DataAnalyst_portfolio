CREATE TABLE sellers (
    seller_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    position VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT true
);

INSERT INTO sellers (first_name, last_name, employee_id, position, hire_date, is_active) VALUES
('Иван', 'Петров', 'EMP001', 'Кассир', '2022-01-15', true),
('Мария', 'Сидорова', 'EMP002', 'Старший кассир', '2021-03-10', true),
('Алексей', 'Козлов', 'EMP003', 'Кассир', '2023-05-20', true),
('Ольга', 'Николаева', 'EMP004', 'Администратор', '2020-11-05', true),
('Дмитрий', 'Васильев', 'EMP005', 'Кассир', '2022-08-12', false);

SELECT * FROM sellers;

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    barcode VARCHAR(50) UNIQUE,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    in_stock BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (product_name, barcode, category, price, unit, in_stock) VALUES
('Хлеб Бородинский', '4601234567890', 'Хлебобулочные изделия', 45.50, 'шт', true),
('Молоко Простоквашино 2.5%', '4602345678901', 'Молочные продукты', 89.90, 'шт', true),
('Яйца куриные С0', '4603456789012', 'Яйца', 125.00, 'уп', true),
('Картофель мытый', '4604567890123', 'Овощи', 65.00, 'кг', true),
('Яблоки Гренни Смит', '4605678901234', 'Фрукты', 149.90, 'кг', true),
('Сыр Российский', '4606789012345', 'Молочные продукты', 450.00, 'кг', true),
('Колбаса Докторская', '4607890123456', 'Колбасные изделия', 320.00, 'кг', true),
('Вода минеральная', '4608901234567', 'Напитки', 35.00, 'шт', false),
('Шоколад Alpen Gold', '4609012345678', 'Кондитерские изделия', 75.50, 'шт', true),
('Кофе Jacobs', '4610123456789', 'Бакалея', 450.00, 'шт', true);

SELECT * FROM products;

CREATE TABLE receipts (
    receipt_id SERIAL PRIMARY KEY,
    receipt_number VARCHAR(20) UNIQUE NOT NULL,
    seller_id INTEGER REFERENCES sellers(seller_id),
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20) CHECK (payment_method IN ('cash', 'card', 'online')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    store_number VARCHAR(10) DEFAULT '005'
);

INSERT INTO receipts (receipt_number, seller_id, total_amount, payment_method, created_at) VALUES
('CHK00123456', 1, 285.40, 'card', '2024-01-15 08:30:15'),
('CHK00123457', 2, 520.90, 'cash', '2024-01-15 09:15:22'),
('CHK00123458', 1, 125.00, 'card', '2024-01-15 10:05:47'),
('CHK00123459', 3, 890.50, 'online', '2024-01-15 11:20:33'),
('CHK00123460', 2, 230.00, 'card', '2024-01-15 12:45:18');

SELECT * FROM receipts;

CREATE TABLE receipt_items (
    item_id SERIAL PRIMARY KEY,
    receipt_id INTEGER REFERENCES receipts(receipt_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity DECIMAL(8,3) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL
);

INSERT INTO receipt_items (receipt_id, product_id, quantity, unit_price, total_price) VALUES
(1, 1, 1, 45.50, 45.50),
(1, 2, 2, 89.90, 179.80),
(1, 10, 1, 60.10, 60.10),

(2, 3, 1, 125.00, 125.00),
(2, 6, 0.5, 450.00, 225.00),
(2, 7, 0.3, 320.00, 96.00),
(2, 9, 2, 75.50, 151.00),

(3, 3, 1, 125.00, 125.00),

(4, 4, 2.5, 65.00, 162.50),
(4, 5, 1.2, 149.90, 179.88),
(4, 6, 0.8, 450.00, 360.00),
(4, 7, 0.6, 320.00, 192.00),

(5, 1, 1, 45.50, 45.50),
(5, 2, 1, 89.90, 89.90),
(5, 9, 1, 75.50, 75.50),
(5, 10, 1, 19.10, 19.10);

CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    current_stock DECIMAL(8,3) NOT NULL,
    min_stock_level DECIMAL(8,3) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO inventory (product_id, current_stock, min_stock_level) VALUES
(1, 50, 10),
(2, 120, 30),
(3, 80, 20),
(4, 200.5, 50),
(5, 150.2, 40),
(6, 25.8, 5),
(7, 18.9, 4),
(8, 0, 20),
(9, 75, 15),
(10, 45, 10);

SELECT * FROM inventory;

-- Топ продаваемых товаров
SELECT 
    p.product_name,
    SUM(ri.quantity) as total_quantity,
    SUM(ri.total_price) as total_revenue
FROM receipt_items ri
JOIN products p ON ri.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_revenue DESC;

-- Продажи по кассирам 
SELECT 
    s.first_name || ' ' || s.last_name as seller_name, -- || ' ' || объединяет имя и фамилию в seller_name 
    COUNT(r.receipt_id) as receipts_count,
    SUM(r.total_amount) as total_sales
FROM receipts r
JOIN sellers s ON r.seller_id = s.seller_id
GROUP BY s.seller_id, seller_name
ORDER BY total_sales DESC;

-- Товары, которых не хватает в магазине и требуется пополнение
SELECT 
    p.product_name,
    i.current_stock,
    i.min_stock_level
FROM inventory i
JOIN products p ON i.product_id = p.product_id
WHERE i.current_stock <= i.min_stock_level;

-- Ежедневная выручка магазина
SELECT 
    DATE(created_at) as sale_date,
    COUNT(*) as receipts_count,
    SUM(total_amount) as daily_revenue
FROM receipts
GROUP BY DATE(created_at)
ORDER BY sale_date DESC;

-- таблицы для связи многие ко многим по условию задания :-)
-- для генерации содержания таблиц я использовал LLM
CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    parent_category_id INTEGER REFERENCES categories(category_id),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Наполнение категориями для "Пятерочка"
INSERT INTO categories (category_name, parent_category_id, description) VALUES
-- Основные категории (родительские)
('Продукты питания', NULL, 'Все пищевые продукты'),
('Бытовая химия', NULL, 'Средства для уборки и гигиены'),
('Хозтовары', NULL, 'Товары для дома'),

-- Подкатегории для "Продукты питания"
('Молочные продукты', 1, 'Молоко, сыры, йогурты'),
('Хлебобулочные изделия', 1, 'Хлеб, булки, выпечка'),
('Мясо и колбасы', 1, 'Мясо, колбасные изделия'),
('Овощи и фрукты', 1, 'Свежие овощи и фрукты'),
('Бакалея', 1, 'Крупы, макароны, консервы'),
('Напитки', 1, 'Соки, воды, газировка'),
('Кондитерские изделия', 1, 'Сладости, шоколад, печенье'),
('Замороженные продукты', 1, 'Заморозка, полуфабрикаты'),

-- Подкатегории для "Молочные продукты"
('Молоко', 4, 'Различные виды молока'),
('Сыры', 4, 'Твердые и мягкие сыры'),
('Йогурты', 4, 'Йогурты, творожки'),
('Кисломолочные продукты', 4, 'Кефир, ряженка, сметана'),

-- Подкатегории для "Бытовая химия"
('Стиральные порошки', 2, 'Средства для стирки'),
('Моющие средства', 2, 'Для мытья посуды и поверхностей'),
('Гигиена', 2, 'Мыло, шампуни, зубные пасты'),

-- Подкатегории для "Хозтовары"
('Посуда', 3, 'Тарелки, кружки, кастрюли'),
('Текстиль', 3, 'Полотенца, постельное белье');

-- Промежуточная таблица для связи Many-to-Many
CREATE TABLE IF NOT EXISTS product_categories (
    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT false, -- основная категория товара
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, category_id)
);

INSERT INTO product_categories (product_id, category_id, is_primary) VALUES
(1, 5, true),
(2, 4, true),
(2, 10, true),
(3, 1, true),
(4, 7, true),
(5, 7, true),
(6, 4, true),
(6, 11, true),
(7, 6, true),
(8, 9, true),
(9, 15, true),
(10, 8, true),
(2, 8, false),
(1, 8, false),
(9, 8, false),
(10, 15, false),
(5, 15, false);

SELECT * FROM product_categories;

-- Товары с их категориями (демонстрация многие-ко-многим)
SELECT 
    p.product_name,
    c.category_name,
    pc.is_primary
FROM products p
JOIN product_categories pc ON p.product_id = pc.product_id
JOIN categories c ON pc.category_id = c.category_id
ORDER BY p.product_name;

-- Очищаем таблицу от некорректных связей
TRUNCATE TABLE product_categories;

-- Создаем правильные связи
INSERT INTO product_categories (product_id, category_id, is_primary) VALUES
-- Хлеб Бородинский (1)
(1, 5, true),   -- Хлебобулочные изделия
(1, 8, false),  -- Бакалея

-- Молоко Простоквашино (2)
(2, 4, true),   -- Молочные продукты
(2, 10, true),  -- Молоко
(2, 8, false),  -- Бакалея

-- Яйца куриные (3)
(3, 1, true),   -- Продукты питания

-- Картофель мытый (4)
(4, 7, true),   -- Овощи и фрукты

-- Яблоки Гренни Смит (5)
(5, 7, true),   -- Овощи и фрукты
(5, 15, false), -- Кондитерские изделия

-- Сыр Российский (6)
(6, 4, true),   -- Молочные продукты
(6, 11, true),  -- Сыры

-- Колбаса Докторская (7)
(7, 6, true),   -- Мясо и колбасы

-- Вода минеральная (8)
(8, 9, true),   -- Напитки

-- Шоколад Alpen Gold (9)
(9, 15, true),  -- Кондитерские изделия
(9, 8, false),  -- Бакалея

-- Кофе Jacobs (10)
(10, 8, true),  -- Бакалея
(10, 15, false); -- Кондитерские изделия

SELECT 
    p.product_name,
    c.category_name,
    pc.is_primary
FROM products p
JOIN product_categories pc ON p.product_id = pc.product_id
JOIN categories c ON pc.category_id = c.category_id
ORDER BY p.product_name, pc.is_primary DESC;
