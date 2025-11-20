# spark_etl_processor/Dockerfile
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/bitnami/spark:3.5.5
WORKDIR /app
# 安装必要的 Python 包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 复制你的 ETL 脚本
COPY main.py .
COPY .. .

CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1,mysql:mysql-connector-java:8.0.28", "/app/etl_script.py"]