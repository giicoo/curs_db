-- 1. order_statuses — фиксированный справочник
INSERT INTO order_statuses (name, sort_order, is_final) VALUES
    ('Оформлен', 1, FALSE),
    ('Собран', 2, FALSE),
    ('В доставке', 3, FALSE),
    ('Доставлен', 4, TRUE),
    ('Отменён', 5, TRUE);

-- 2. product_types — фиксированный справочник
INSERT INTO product_types (name) VALUES
    ('Электроника'), ('Одежда и обувь'), ('Дом и сад'), ('Книги'),
    ('Спорт и отдых'), ('Детские товары'), ('Косметика'),
    ('Продукты питания'), ('Автотовары'), ('Зоотовары');

-- 3. users — 350 записей (300 покупателей + 50 продавцов)
-- Единый тестовый пароль для ВСЕХ сгенерированных пользователей: Test1234!
-- Хеш сгенерирован реальной библиотекой argon2-cffi (PasswordHasher().hash('Test1234!'))
INSERT INTO users (login, password_hash, email, registered_at)
SELECT
    'user' || g.id,
    '$argon2id$v=19$m=65536,t=3,p=4$+LATyBqSk8yC+c/8sS83RQ$xomysnefUE0LH35TcOtKKSCUdlRYEkSzkEspU4DSGlQ',
    'user' || g.id || '@example.com',
    NOW() - (random() * 730)::int * INTERVAL '1 day'
FROM generate_series(1, 350) AS g(id);

-- 4. customers — первые 300 пользователей
INSERT INTO customers (user_id, last_name, first_name, phone, delivery_address)
SELECT
    u.id,
    (ARRAY['Иванов','Петров','Сидоров','Смирнов','Кузнецов',
           'Попов','Васильев','Соколов','Михайлов','Новиков'])[1 + (random()*9)::int],
    (ARRAY['Александр','Дмитрий','Максим','Сергей','Андрей',
           'Алексей','Артём','Илья','Кирилл','Михаил'])[1 + (random()*9)::int],
    '+375' || (290000000 + (random()*9999999)::int)::text,
    (ARRAY['Минск','Гомель','Витебск','Гродно','Брест','Могилёв'])[1 + (random()*5)::int]
        || ', ул. ' || (ARRAY['Ленина','Победы','Советская','Заслонова','Куйбышева'])[1 + (random()*4)::int]
        || ', д. ' || (1 + (random()*100)::int)
FROM users u
WHERE u.id <= 300;

-- 5. sellers — последние 50 пользователей
INSERT INTO sellers (user_id, name, description, registered_at)
SELECT
    u.id,
    'Магазин №' || (u.id - 300),
    'Продавец товаров категории ' ||
        (ARRAY['Электроника','Одежда','Дом и сад','Книги','Спорт'])[1 + (random()*4)::int],
    CURRENT_DATE - (random()*1000)::int
FROM users u
WHERE u.id > 300;

-- 6. products — 400 записей
INSERT INTO products (seller_id, type_id, name, price, stock_quantity)
SELECT
    1 + (random() * 49)::int,
    1 + (random() * 9)::int,
    'Товар №' || g.id,
    (10 + random() * 990)::numeric(10,2),
    (random() * 200)::int
FROM generate_series(1, 400) AS g(id);

-- 7. orders — 600 записей
INSERT INTO orders (customer_id, status_id, order_date, delivery_address)
SELECT
    c.id,
    1 + (random() * 4)::int,
    NOW() - (random() * 365)::int * INTERVAL '1 day',
    c.delivery_address
FROM (
    SELECT (1 + (random() * 299)::int) AS cust_pick
    FROM generate_series(1, 600)
) picks
JOIN customers c ON c.id = picks.cust_pick;

-- 8. order_items — 1-3 позиции на заказ, без дублей по составному ключу
INSERT INTO order_items (order_id, product_id, quantity, price_at_order)
SELECT o.id, p.id, 1 + (random() * 2)::int, p.price
FROM orders o
CROSS JOIN LATERAL (
    SELECT id, price FROM products
    ORDER BY random()
    LIMIT (1 + (random() * 2)::int)
) p
ON CONFLICT (order_id, product_id) DO NOTHING;

-- 9. reviews — 500 записей
INSERT INTO reviews (customer_id, product_id, rating, comment_text, created_at)
SELECT
    1 + (random() * 299)::int,
    1 + (random() * 399)::int,
    1 + (random() * 4)::int,
    (ARRAY[
        'Отличный товар, рекомендую!',
        'Качество соответствует цене.',
        'Доставка задержалась, но товар хороший.',
        'Не совсем то, что ожидал.',
        'Буду заказывать ещё.'
    ])[1 + (random() * 4)::int],
    CURRENT_DATE - (random() * 365)::int
FROM generate_series(1, 500) AS g(id);
