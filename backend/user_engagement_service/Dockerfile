FROM python:3.8

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

EXPOSE 5003

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5003"]