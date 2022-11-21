CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    tg_id BIGINT
);

CREATE TABLE IF NOT EXISTS likes(
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    comment_id VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS favorites(
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    comment_id VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS comments(
    id SERIAL PRIMARY KEY,
    author_id INTEGER,
    comment_id VARCHAR(255),
    topic_id VARCHAR(255)
);