// src/main.js
import { createApp } from "vue";
import { createPinia } from 'pinia'; // 导入 Pinia
import App from "./App.vue";
import router from "./router";

const app = createApp(App);
app.use(router);

// 创建 Pinia 实例并让整个应用使用它
const pinia = createPinia();
app.use(pinia);

app.mount("#app");