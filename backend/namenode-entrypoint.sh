#!/bin/bash

# 检查 NameNode 数据目录是否已格式化
if [ ! -d "/hadoop/dfs/name/current" ]; then
  echo "NameNode data directory not formatted. Formatting now..."
  hdfs namenode -format -nonInteractive
else
  echo "NameNode data directory already formatted. Skipping format."
fi

# 启动 NameNode 服务
hdfs namenode