FROM python:3.8

WORKDIR /app

# 先复制 requirements.txt 并安装依赖，利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 明确复制 Flask 应用主文件
# 由于 Dockerfile 在 book_manage/ 目录下，app.py 也在 book_manage/ 目录下
# 所以 app.py 相对于 Dockerfile 的路径就是 app.py
COPY . .

# --- 关键修改点：调整 COPY 源路径 ---
# 因为 Dockerfile 位于 book_manage/ 目录下，而 books.csv 位于 data/books.csv
# 相对于 Dockerfile，books.csv 的路径就是 data/books.csv
COPY data/books.csv .

# 复制整个应用目录到容器的工作目录
# 这一行非常关键，它会复制 app.py, routes/, models/ 等所有内容
COPY . .

# CMD 是容器启动时执行的命令
# 如果你的 Flask 应用主文件是 app.py，直接运行它
CMD ["python", "app.py"]