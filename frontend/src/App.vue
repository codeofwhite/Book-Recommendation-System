<template>
  <div id="app">
    <nav class="main-nav">
      <router-link to="/" class="nav-item">首页</router-link>
      <router-link to="/books" class="nav-item">图书列表</router-link>
      <router-link to="/about" class="nav-item">关于我们</router-link>
      <router-link to="/auth" class="nav-item login-button">登录</router-link>
    </nav>

    <main class="app-content">
      <router-view/>
    </main>

    <footer class="main-footer">
      <p>&copy; 2025 图书管理系统. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup>

</script>

<style>
/* 全局样式或 App.vue 特有样式 */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  min-height: 100vh; /* 让内容撑满整个视口高度 */
  display: flex;
  flex-direction: column; /* 垂直布局，让页脚固定在底部 */
}

.main-nav {
  padding: 15px 20px;
  background-color: #34495e; /* 深蓝色背景 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center; /* 导航项居中 */
  align-items: center;
}

.nav-item {
  font-weight: bold;
  color: #ecf0f1; /* 浅灰色文字 */
  text-decoration: none;
  margin: 0 15px;
  padding: 5px 0;
  transition: color 0.3s ease;
}

.nav-item:hover,
.nav-item.router-link-exact-active {
  color: #42b983; /* 绿色高亮 */
}

/* 登录按钮样式 */
.login-button {
  background-color: #28a745; /* 绿色按钮 */
  color: white;
  padding: 8px 15px;
  border-radius: 5px;
  margin-left: 30px; /* 与其他导航项保持距离 */
  transition: background-color 0.3s ease;
}

.login-button:hover {
  background-color: #218838;
}

.app-content {
  flex-grow: 1; /* 让主要内容区域占据所有可用空间，将页脚推到底部 */
  padding: 20px; /* 内容区域内边距 */
}

.main-footer {
  padding: 15px;
  background-color: #34495e;
  color: #ecf0f1;
  font-size: 0.9em;
  margin-top: auto; /* 将页脚推到底部 */
}
</style>