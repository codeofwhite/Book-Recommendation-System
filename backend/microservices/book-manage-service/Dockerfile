FROM python:3.8

WORKDIR /app

# 复制 requirements.txt 并安装依赖，利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用所有文件到工作目录
COPY . .

CMD ["python", "app.py"]