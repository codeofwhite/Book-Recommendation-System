import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // 代理到运行在 5000 端口的微服务
      "/service-a": {
        target: "http://132.232.210.47:5000",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/service-a/, ""), // 重写路径，移除 /service-a 前缀
      },
      // 代理到运行在 5001 端口的微服务
      "/service-b": {
        target: "http://132.232.210.47:5001",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/service-b/, ""), // 重写路径，移除 /service-b 前缀
      },
      // 如果还有其他微服务，可以继续添加...
      // "/service-c": {
      //   target: "http://localhost:5002",
      //   changeOrigin: true,
      //   secure: false,
      //   rewrite: (path) => path.replace(/^\/service-c/, ""),
      // },
    },
  },
  base: "/",
});