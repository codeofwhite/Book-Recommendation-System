import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      "/api": {
        // Any request starting with /api (e.g., /api/auth/login, /api/books)
        target: "http://localhost:5000", // Points to your API Gateway
        changeOrigin: true, // Needed for virtual hosting sites
        secure: false, // If your backend doesn't use HTTPS (common in dev)
        // rewrite: (path) => path.replace(/^\/api/, '/api'), // Often not needed if gateway already expects /api
      },
    },
  },
  base: "/",
});
