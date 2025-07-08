// vite.config.js (无需修改，保留现有内容即可)
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { devProxy, prodProxy, ZHJProxy } from "./config"; // 导入所有配置

export default defineConfig(({ mode }) => {
  let currentProxy = devProxy; // 默认使用 devProxy

  if (mode === "production") {
    currentProxy = prodProxy;
  } else if (mode === "zhj") { // 根据模式选择 ZHJProxy
    currentProxy = ZHJProxy;
  }

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
        "/service-b": { // 这一行已经存在，Admin前端会使用它
          target: currentProxy.targetB,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/service-b/, ""),
        },
        "/service-c": {
          target: currentProxy.targetC,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/service-c/, ""),
        },
      },
    },
    base: "/",
  };
});