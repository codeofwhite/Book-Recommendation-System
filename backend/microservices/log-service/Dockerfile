# log_service/Dockerfile
# 使用轻量级的 Python 官方镜像作为基础
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 到容器，并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 复制整个 log_service 目录到容器
COPY . .

# 暴露 Flask 应用运行的端口
EXPOSE 5006

# 定义容器启动时执行的命令
# KAFKA_BROKER_URL 会在 docker-compose.yml 中通过 environment 传入
CMD ["python", "app.py"]