# datax_worker/Dockerfile
# 使用一个包含 Java 运行环境的基础镜像
# OpenJDK 11 或 8 都可以，DataX 对 Java 版本要求不高
FROM openjdk:11-jre-slim

# 更新包列表并安装 Python3 和 pip
# 'apt-get update' 和 'apt-get install -y python3 python3-pip' 是在基于 Debian/Ubuntu 的镜像中安装 Python 的标准做法
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置 Python 别名，确保 'python' 命令指向 python3
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# 设置工作目录
WORKDIR /app

# 将 DataX 发行包复制到容器中并解压
# 假设你在宿主机的 `datax_worker` 目录旁放置了 `datax.tar.gz`
# 建议将 DataX 发行包放在 `datax_worker` 目录下，或者通过 COPY --from 方式引入
COPY datax.tar.gz .
RUN tar -xzf datax.tar.gz && rm datax.tar.gz

# 设置 DataX 的主目录环境变量
ENV DATAX_HOME=/app/datax

# 安装 MySQL JDBC 驱动（因为你要从 MySQL 抽取数据）
# 你可以从 Maven Central 下载：https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.28/mysql-connector-java-8.0.28.jar
# 将下载的 .jar 文件放在 datax_worker/jdbc_drivers 目录下
COPY jdbc_drivers/mysql-connector-java-8.0.28.jar ${DATAX_HOME}/plugin/reader/mysqlreader/libs/
COPY jdbc_drivers/mysql-connector-java-8.0.28.jar ${DATAX_HOME}/plugin/writer/mysqlwriter/libs/

# 如果你还需要 MongoDB Reader/Writer，也需要下载并放置相应的驱动
# MongoDB DataX 插件通常需要额外安装，或者使用 DataX 提供的 MongoDB 插件
# DataX 自带的 mongodbreader/writer plugin 已经包含了大部分依赖，如果不能用，可能需要手动添加 MongoDB Java Driver
# COPY jdbc_drivers/mongo-java-driver-xxx.jar ${DATAX_HOME}/plugin/reader/mongodbreader/libs/

# 定义容器启动时运行的默认命令，保持容器存活以便我们进入执行任务
CMD ["tail", "-f", "/dev/null"]