# 前提条件
1. 方法一：安装 Windows Docker Desktop。安装 WSL，然后开发环境选择 Ubuntu。
2. 方法二：安装 Windows Docker Desktop。直接在 Windows 上开发也无所谓。

# 怎么用这个后端？
1. 首先命令行 cd 到 backend
2. 使用命令 启动 docker 服务
```bash
docker compose up -d --build
```
3. 查看你的 Docker Destop 然后可以看到各个微服务的启动
4. cd 到 frontend 里面，写入命令
```bash
npm run dev
```
5. 结束！可以看到完整的页面显示了

看topic：docker exec kafka kafka-topics --bootstrap-server kafka:29092 --list