FROM python:3.13.3-slim

WORKDIR /app

# 1. Cài đặt các phụ thuộc hệ thống trước
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# 2. Cài đặt uv (astral.sh) trước
RUN curl -Ls https://astral.sh/uv/install.sh | sh && \
    mv "$HOME/.local/bin/uv" /usr/local/bin/uv

# 3. Copy requirements và cài đặt các phụ thuộc khác + uvicorn + uvloop
COPY requirements.txt .
RUN uv venv /app/venv && \
    . /app/venv/bin/activate && \
    uv pip install --no-cache-dir -r requirements.txt && \
    uv pip install --no-cache-dir uvicorn[standard] && \
    /app/venv/bin/uvicorn --version

# 4. Copy mã nguồn
COPY ./app ./app

EXPOSE 8000

# 5. Chạy ứng dụng
CMD ["/app/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "16"]
