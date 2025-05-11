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



-- Kiểm tra các extension đã cài đặt
SELECT * FROM pg_extension;
-- Tạo index cho tìm kiếm
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_students_name_trgm ON students USING gin (name gin_trgm_ops);

-- Ràng buộc UNIQUE mạnh mẽ hơn
ALTER TABLE students DROP CONSTRAINT IF EXISTS students_email_key;
ALTER TABLE students ADD CONSTRAINT unique_student_email
UNIQUE (email)
DEFERRABLE INITIALLY DEFERRED;

-- Index cho các trường thường dùng
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_id);
CREATE INDEX IF NOT EXISTS idx_students_dob ON students(date_of_birth);


CREATE INDEX idx_users_email ON users(email);
