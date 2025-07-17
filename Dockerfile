FROM python:3.13.3-slim

WORKDIR /app

# 1. Cài đặt các phụ thuộc hệ thống cần thiết và xóa build-essential sau khi dùng
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential && \
    curl -Ls https://astral.sh/uv/install.sh | sh && \
    mv "$HOME/.local/bin/uv" /usr/local/bin/uv && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN uv venv /app/venv && \
    . /app/venv/bin/activate && \
    uv pip install --no-cache-dir -r requirements.txt && \
    uv pip install --no-cache-dir uvicorn[standard]
COPY .env .env
COPY ./app ./app

EXPOSE 8000

# Tạo user non-root để tăng bảo mật
RUN useradd -m appuser
USER appuser

CMD ["/app/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
