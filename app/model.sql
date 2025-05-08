CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    grade TEXT,
    teacher_name TEXT
);

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    date_of_birth DATE,
    class_id INTEGER REFERENCES classes(id) ON DELETE SET NULL
);


