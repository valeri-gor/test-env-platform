CREATE TABLE IF NOT EXISTS appointments (
                                            id SERIAL PRIMARY KEY,
                                            client_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    slot_time VARCHAR(50) NOT NULL,
    status VARCHAR(30) DEFAULT 'confirmed'
    );

INSERT INTO appointments (client_name, email, slot_time) VALUES
                                                             ('Тестовый Пользователь 1', 'user1@example.test', '2026-11-25 10:00'),
                                                             ('Тестовый Пользователь 2', 'user2@example.test', '2026-11-25 11:00');
