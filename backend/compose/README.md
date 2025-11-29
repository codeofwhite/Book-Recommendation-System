## 部署与启动命令指南

以下是项目依赖镜像的管理和核心服务的启动命令。

### 1\. 镜像管理策略

  * 如果 Docker Compose 在尝试基于 **`Dockerfile`** 构建或拉取镜像时遇到网络或权限问题（`pull` 失败），请采取**手动拉取**操作。
  * **版本确认：** 项目中使用的组件版本已确定。如果自动拉取失败，请使用命令行手动执行 `docker pull <image_name>:<tag>` 拉取必要的镜像，然后再尝试启动服务。

### 2\. 服务启动命令

所有服务都通过 Docker Compose 进行统一部署和启动。

#### 2.1. 首次启动或正常更新（推荐）

使用以下命令启动所有服务，并将其置于后台运行：

```bash
docker-compose -f auth-service.yml \
               -f base.yml \
               -f book-service.yml \
               -f data-pipeline.yml \
               -f recommendation.yml \
               -f storage.yml \
               -f user-engagement.yml \
               up -d
```

#### 2.2. 强制重建和刷新（代码更新未生效时使用）

如果在本地修改了代码或 `Dockerfile`，但启动后变动未生效，请使用以下命令进行**强制刷新、重建镜像并重新创建容器**：

```bash
docker-compose -f auth-service.yml \
               -f base.yml \
               -f book-service.yml \
               -f data-pipeline.yml \
               -f recommendation.yml \
               -f storage.yml \
               -f user-engagement.yml \
               up -d --build --force-recreate
```

> **参数说明：**
>
>   * `--build`: 强制重建依赖 `Dockerfile` 的服务镜像。
>   * `--force-recreate`: 强制停止并重新创建所有服务容器。