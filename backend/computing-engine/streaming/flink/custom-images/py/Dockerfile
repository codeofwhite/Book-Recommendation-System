# flink_py_image/Dockerfile
# 基于官方 Flink Java/Scala 镜像
FROM apache/flink:1.17.1-scala_2.12

# 安装 Python 和 pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# 创建 'python' 命令的软链接
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# 设置 Python 路径
ENV PATH="/usr/bin:${PATH}"
ENV PYTHONIOENCODING="UTF-8"

# --- 使用清华大学 PyPI 镜像源安装 Python 包 ---

# 安装 PyFlink
RUN pip3 install apache-flink==1.17.1 -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 安装其他 PyFlink Job 可能需要的 Python 库
RUN pip3 install redis -i https://pypi.tuna.tsinghua.edu.cn/simple/

RUN pip install numpy==1.23.5 --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 设置 PyFlink 相关环境变量
ENV FLINK_PYTHON_FN_EXECUTION_MODE="PROCESS"
ENV PYFLINK_PYTHON_ENV="/usr/bin/python3"
ENV PYFLINK_CLIENT_EXECUTABLE="/usr/bin/python3"
ENV PYFLINK_STREAM_ENVIRONMENT_JAVA_OPTS="-Xmx1024m"

# 如果你的 PyFlink Job 会用到其他的 Python 包，可以把它们写到 requirements.txt
# COPY requirements.txt /tmp/
# RUN pip3 install -r /tmp/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/