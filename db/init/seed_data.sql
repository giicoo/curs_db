-- 1. order_statuses
INSERT INTO order_statuses (name, sort_order, is_final) VALUES
    ('Оформлен', 1, FALSE),
    ('Собран', 2, FALSE),
    ('В доставке', 3, FALSE),
    ('Доставлен', 4, TRUE),
    ('Отменён', 5, TRUE);

-- 2. product_types
INSERT INTO product_types (name) VALUES
    ('Электроника'), ('Одежда и обувь'), ('Дом и сад'), ('Книги'),
    ('Спорт и отдых'), ('Детские товары'), ('Косметика'),
    ('Продукты питания'), ('Автотовары'), ('Зоотовары');

-- 3. users — 350 записей
INSERT INTO users (login, password_hash, email, registered_at)
SELECT
    'user' || g.id,
    '$argon2id$v=19$m=65536,t=3,p=4$+LATyBqSk8yC+c/8sS83RQ$xomysnefUE0LH35TcOtKKSCUdlRYEkSzkEspU4DSGlQ',
    'user' || g.id || '@example.com',
    NOW() - (random() * 730)::int * INTERVAL '1 day'
FROM generate_series(1, 350) AS g(id);

-- 4. customers — первые 300
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
FROM users u WHERE u.id <= 300;

-- 5. sellers — последние 50 с осмысленными названиями
INSERT INTO sellers (user_id, name, description, registered_at)
SELECT
    u.id,
    (ARRAY[
        'ТехноМир', 'МодаСтиль', 'ДомОчаг', 'КнижныйДом', 'СпортЛига',
        'ДетскийМирPro', 'БьютиLab', 'ВкусноМаркет', 'АвтоПлюс', 'ЗооДруг',
        'МегаМаркет', 'ПремиумТовары', 'ЭкоМаркет', 'ТопДил', 'ФастШоп',
        'БюджетМаркет', 'ЛюксТовары', 'НеоМаркет', 'ПраймShop', 'КвикМаркет',
        'ВиталМаркет', 'СмартБай', 'ДэйлиШоп', 'МегаСклад', 'ПрямоСклад',
        'ТрендМаркет', 'АлмазТорг', 'РосТовар', 'БелМаркет', 'ЕвроШоп',
        'ГудПрайс', 'КэшБэкМаркет', 'СэйвМор', 'БигДил', 'СупермаркетX',
        'МаксиМаркет', 'МиниПрайс', 'ОллМаркет', 'ПанМаркет', 'АльфаШоп',
        'БетаМаркет', 'ГаммаShop', 'ДельтаПрайс', 'ОмегаМаркет', 'СигмаШоп',
        'ТетаМаркет', 'ЗетаShop', 'КаппаПрайс', 'ЛямбдаМаркет', 'МюШоп'
    ])[u.id - 300],
    'Качественные товары по доступным ценам. Быстрая доставка по всей стране.',
    CURRENT_DATE - (random()*1000)::int
FROM users u WHERE u.id > 300;

-- 6. products — 500 записей, 50 на категорию, осмысленные названия
INSERT INTO products (seller_id, type_id, name, price, stock_quantity)
SELECT
    (1 + (random() * 49)::int)::int,
    cat.type_id,
    cat.name_arr[1 + (random() * 9)::int]
        || ' ' || (ARRAY['Pro', 'Lite', 'Plus', 'Max', 'Mini', 'Air', 'Ultra', 'Basic', 'Premium', 'Sport'])[1 + (random() * 9)::int],
    (cat.min_p + random() * (cat.max_p - cat.min_p))::numeric(10,2),
    (5 + random() * 175)::int
FROM (
    VALUES
        (1, ARRAY['Смартфон', 'Ноутбук', 'Планшет', 'Наушники TWS', 'Умные часы', 'Bluetooth-колонка', 'Веб-камера', 'Игровая мышь', 'Клавиатура', 'Фитнес-браслет']::text[], 300::numeric, 5000::numeric),
        (2, ARRAY['Куртка зимняя', 'Джинсы slim', 'Кроссовки', 'Рюкзак городской', 'Летнее платье', 'Свитер оверсайз', 'Осеннее пальто', 'Вязаная шапка', 'Кожаные перчатки', 'Шерстяной шарф']::text[], 500::numeric, 3500::numeric),
        (3, ARRAY['Садовые ножницы', 'Шланг поливочный', 'Цветочный горшок', 'Набор для пикника', 'Лейка', 'Садовый фонарь', 'Семена томатов', 'Удобрение', 'Садовые перчатки', 'Складная лопата']::text[], 150::numeric, 2000::numeric),
        (4, ARRAY['Python для начинающих', 'Роман-бестселлер', 'Детектив зарубежный', 'Кулинарная книга', 'Книга по психологии', 'Атлас мира', 'Англо-русский словарь', 'Книга рецептов', 'Фантастика (том 1)', 'Биография']::text[], 200::numeric, 1500::numeric),
        (5, ARRAY['Гантели 5кг', 'Коврик для йоги', 'Складной велосипед', 'Теннисная ракетка', 'Боксёрские перчатки', 'Скакалка', 'Спортивный термос', 'Пояс для бега', 'Спортивная бутылка', 'Резинки для фитнеса']::text[], 200::numeric, 3000::numeric),
        (6, ARRAY['Конструктор LEGO', 'Мягкая игрушка', 'Набор для рисования', 'Пазл 500 деталей', 'Кукла', 'Машинка р/у', 'Детский велосипед', 'Самокат', 'Книга-раскраска', 'Детская палатка']::text[], 300::numeric, 2500::numeric),
        (7, ARRAY['Крем для лица', 'Шампунь питательный', 'Маска для волос', 'Тональный крем', 'Тушь для ресниц', 'Матовая помада', 'Женские духи', 'Мужской парфюм', 'Скраб для тела', 'Гель для умывания']::text[], 300::numeric, 2000::numeric),
        (8, ARRAY['Кофе молотый', 'Травяной чай', 'Орехи ассорти', 'Горький шоколад', 'Натуральный мёд', 'Протеиновый батончик', 'Сухофрукты mix', 'Оливковое масло', 'Соус песто', 'Растворимый кофе']::text[], 100::numeric, 800::numeric),
        (9, ARRAY['Автомобильный пылесос', 'Видеорегистратор', 'GPS-навигатор', 'Чехол на руль', 'Коврики в авто', 'Автозарядка USB', 'Освежитель воздуха', 'Антифриз 5л', 'Щётка для снега', 'Компрессор']::text[], 200::numeric, 3000::numeric),
        (10, ARRAY['Корм для собак', 'Корм для кошек', 'Игрушка для кошки', 'Домик для кота', 'Кожаный поводок', 'Нержавеющая миска', 'Лежак для питомца', 'Переноска для кота', 'Капли от блох', 'Когтеточка']::text[], 300::numeric, 1500::numeric)
) AS cat(type_id, name_arr, min_p, max_p)
CROSS JOIN generate_series(1, 50);

-- 7. orders — 1650 записей с сезонными пиками

-- Базовый поток: 1200 заказов равномерно за последние 13 месяцев
INSERT INTO orders (customer_id, status_id, order_date, delivery_address)
SELECT
    c.id,
    1 + (random() * 4)::int,
    NOW() - (random() * 400)::int * INTERVAL '1 day',
    c.delivery_address
FROM (
    SELECT (1 + (random() * 299)::int)::int AS cust_pick
    FROM generate_series(1, 1200)
) picks
JOIN customers c ON c.id = picks.cust_pick;

-- Новогодний пик (ноябрь–декабрь 2025, примерно 170–230 дней назад от 2026-06-23)
INSERT INTO orders (customer_id, status_id, order_date, delivery_address)
SELECT
    c.id,
    1 + (random() * 4)::int,
    NOW() - (170 + (random() * 60)::int) * INTERVAL '1 day',
    c.delivery_address
FROM (
    SELECT (1 + (random() * 299)::int)::int AS cust_pick
    FROM generate_series(1, 300)
) picks
JOIN customers c ON c.id = picks.cust_pick;

-- Весенний пик (март 2026, примерно 85–115 дней назад)
INSERT INTO orders (customer_id, status_id, order_date, delivery_address)
SELECT
    c.id,
    1 + (random() * 4)::int,
    NOW() - (85 + (random() * 30)::int) * INTERVAL '1 day',
    c.delivery_address
FROM (
    SELECT (1 + (random() * 299)::int)::int AS cust_pick
    FROM generate_series(1, 150)
) picks
JOIN customers c ON c.id = picks.cust_pick;

-- 8. order_items — 2–4 позиции на заказ (через cross join без LATERAL, чтобы random() пересчитывался на каждой строке)
INSERT INTO order_items (order_id, product_id, quantity, price_at_order)
SELECT DISTINCT ON (t.order_id, t.product_id)
    t.order_id,
    t.product_id,
    1 + floor(random() * 3)::int AS quantity,
    p.price
FROM (
    SELECT
        o.id                                  AS order_id,
        1 + floor(random() * 500)::int        AS product_id
    FROM orders o
    CROSS JOIN generate_series(1, 4) AS g(n)
) t
JOIN products p ON p.id = t.product_id
ORDER BY t.order_id, t.product_id
ON CONFLICT (order_id, product_id) DO NOTHING;

-- 9. reviews — 800 записей с расширенными комментариями
INSERT INTO reviews (customer_id, product_id, rating, comment_text, created_at)
SELECT
    (1 + (random() * 299)::int)::int,
    (1 + (random() * 499)::int)::int,
    1 + (random() * 4)::int,
    (ARRAY[
        'Отличный товар, рекомендую всем!',
        'Качество полностью соответствует цене.',
        'Доставка немного задержалась, но товар хороший.',
        'Не совсем то, что ожидал, но в целом нормально.',
        'Буду заказывать снова, всё понравилось.',
        'Упаковка немного повреждена, сам товар целый.',
        'Превзошёл ожидания! Очень доволен покупкой.',
        'Среднее качество за такую цену.',
        'Быстрая доставка, хороший продавец.',
        'Товар полностью соответствует описанию.'
    ])[1 + (random() * 9)::int],
    CURRENT_DATE - (random() * 365)::int
FROM generate_series(1, 800) AS g(id);
