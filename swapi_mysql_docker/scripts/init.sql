-- Optional: create extra user/table logic at DB init (Airflow task also ensures table exists)
CREATE TABLE IF NOT EXISTS people (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    height VARCHAR(32),
    mass VARCHAR(32),
    hair_color VARCHAR(64),
    skin_color VARCHAR(64),
    eye_color VARCHAR(64),
    birth_year VARCHAR(32),
    gender VARCHAR(32),
    created DATETIME,
    edited DATETIME
);
