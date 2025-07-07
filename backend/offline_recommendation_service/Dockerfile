# 使用官方 Python 镜像作为基础
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个应用代码
COPY . .

# 暴露 Flask 服务的端口
EXPOSE 5005

# 定义环境变量（也可以在 docker-compose.yml 中设置）
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5005

# 启动 Flask 应用
# 这里的 command 假设 app.py 中有 Flask app 的入口
# 如果你是通过 Flask run 启动，可以是：CMD ["flask", "run"]
# 但由于我们有定时任务，直接运行 app.py 脚本更合适
CMD ["python", "app.py"]