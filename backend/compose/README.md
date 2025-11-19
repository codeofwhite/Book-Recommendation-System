- 如果镜像在 dockerfile 的，pull 不下来就手动命令行 pull，现在这些组件的版本确定了一下应该都可以手动 pull。

- 启动命令
```bash
docker-compose -f auth-service.yml -f base.yml -f book-service.yml -f data-pipeline.yml -f recommendation.yml -f storage.yml -f user-engagement.yml up -d
```