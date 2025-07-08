// vite.config.js
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
// 导入所有定义好的代理配置
import { devProxy, prodProxy, ZHJProxy } from "./config";

// Vite 配置定义函数，它接收一个包含 `mode` 的对象
export default defineConfig(({ mode }) => {
  let currentProxy = devProxy; // 默认情况下，使用开发环境的代理配置

  // 根据当前 Vite 的运行模式选择对应的代理配置
  if (mode === "production") {
    // 如果是生产模式 (npm run build)，则使用生产环境配置
    currentProxy = prodProxy;
  } else if (mode === "zhj") {
    // 如果是自定义的 'zhj' 模式，则使用 ZHJ 环境配置
    // 你需要在 package.json 中定义 "vite --mode zhj" 这样的命令来触发此模式
    currentProxy = ZHJProxy;
  }

  return {
    // 注册 Vue 插件
    plugins: [vue()],
    // 开发服务器配置
    server: {
      host: '0.0.0.0', // 允许外部网络访问开发服务器，方便在移动设备或局域网内测试
      port: 5173,      // 开发服务器运行的端口
      proxy: {
        /**
         * 代理规则：当前端请求以 '/service-a' 开头时，将其代理到 targetA 定义的地址。
         * 例如：前端请求 /service-a/api/auth/login 会被代理到 http://localhost:5000/api/auth/login
         * changeOrigin: true 更改请求头中的 Host 字段为目标 URL，这是跨域代理的常见需求。
         * secure: false 允许代理 HTTPS 目标，即使证书无效。在开发环境中常用。
         * rewrite: (path) => path.replace(/^\/service-a/, "") 将请求路径中的 '/service-a' 前缀移除，
         * 因为后端服务通常不需要这个前缀。
         */
        "/service-a": {
          target: currentProxy.targetA, // 认证服务
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/service-a/, ""),
        },
        "/service-b": {
          target: currentProxy.targetB, // 书籍管理服务
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/service-b/, ""),
        },
        "/service-c": {
          target: currentProxy.targetC, // 用户参与服务
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/service-c/, ""),
        },
        "/service-d": {
          // 这是旧的推荐服务代理，现在不再用于离线推荐，但保留以防万一
          target: currentProxy.targetD, 
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/service-d/, ""),
        },
        "/service-e": {
          // 这是日志服务代理
          target: currentProxy.targetE, 
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/service-e/, ""),
        },
        // Flask 应用的 Redis 数据查看器接口代理 (实时推荐)
        "/service-f": {
          target: currentProxy.targetF, 
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/service-f/, ""),
        },
        // 【新增】离线推荐服务代理
        "/service-g": {
          target: currentProxy.targetG, // 离线推荐服务
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/service-g/, ""),
        },
      },
    },
    // 应用的基础路径，部署到非根目录时可能需要设置
    base: "/",
  };
});