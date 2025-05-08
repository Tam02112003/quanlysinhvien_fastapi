FROM python:3.13.3-slim

WORKDIR /app

# Cài curl và các gói cần thiết khác
RUN apt-get update && apt-get install -y curl build-essential

# Tải và cài đặt uv
RUN curl -Ls https://astral.sh/uv/install.sh | sh

# Kiểm tra và di chuyển tệp nhị phân uv
RUN UV_PATH="$HOME/.local/bin/uv" && \
    if [ -f "$UV_PATH" ]; then \
        mv "$UV_PATH" /usr/local/bin/uv; \
    else \
        echo "Cài đặt uv thất bại"; \
        exit 1; \
    fi

# Copy file requirements
COPY requirements.txt .

# Tạo môi trường ảo và cài đặt các thư viện trong cùng một lệnh RUN
RUN uv venv /app/venv && \
    . /app/venv/bin/activate && \
    uv pip install --no-cache-dir -r requirements.txt && \
    /app/venv/bin/uvicorn --version

# Copy mã nguồn ứng dụng
COPY ./app ./app

EXPOSE 8000

# Chạy uvicorn server
CMD ["/app/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]