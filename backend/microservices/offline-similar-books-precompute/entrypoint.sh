#!/bin/sh

# 先执行一次初始化
python /app/offline_precompute_similar_books.py

# 启动cron服务
echo "Starting cron service..."
echo "$CRON_SCHEDULE python /app/offline_precompute_similar_books.py >> /var/log/similar_books_precompute.log 2>&1" > /etc/crontabs/root
crond -l 2 -f