import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { devProxy, prodProxy } from "./config"; // 导入配置

export default defineConfig(({ mode }) => {
  // 根据模式选择代理配置
  const currentProxy = mode === "development" ? devProxy : prodProxy;

  return {
    plugins: [vue()],
    server: {
      proxy: {
        "/service-a": {
          target: currentProxy.targetA,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/service-a/, ""),
        },
        "/service-b": {
          target: currentProxy.targetB,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/service-b/, ""),
        },
      },
    },
    base: "/",
  };
});