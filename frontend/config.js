// config.js

/**
 * 开发环境代理配置
 * 所有服务均指向本地 localhost 端口
 */
const devProxy = {
  // targetA: 用户认证服务，通常是登录、注册、用户信息等
  targetA: "http://localhost:5000",
  // targetB: 书籍管理服务，例如书籍列表、详情、搜索等
  targetB: "http://localhost:5001",
  // targetC: 用户参与服务，例如点赞、收藏、评论等
  targetC: "http://localhost:5003",
  // targetD: 推荐服务 (旧的离线推荐或通用推荐)，目前未使用
  targetD: "http://localhost:5002",
  // targetE: 日志服务，用于接收前端埋点数据
  targetE: "http://localhost:5006",
  targetF: "http://localhost:5004", // 实时推荐 (Flask 应用)
  targetG: "http://localhost:5005", // 【新增】离线推荐服务
};

/**
 * ZHJ 环境代理配置 (可能是某个特定开发或测试环境)
 * 所有服务均指向指定 IP 地址的端口
 */
const ZHJProxy = {
  targetA: "http://10.242.30.147:5000",
  targetB: "http://10.242.30.147:5001",
  targetC: "http://10.242.30.147:5003",
  targetD: "http://10.242.30.147:5002",
  targetE: "http://10.242.30.147:5006", // 示例
  targetF: "http://10.242.30.147:5004",
  targetG: "http://10.242.30.147:5005", // 【新增】离线推荐服务
};

/**
 * 生产环境代理配置
 * 所有服务均指向生产环境的 IP 地址或域名端口
 */
const prodProxy = {
  targetA: "http://132.232.210.47:5000",
  targetB: "http://132.232.210.47:5001",
  targetC: "http://132.232.210.47:5003",
  targetD: "http://132.232.210.47:5002",
  targetE: "http://132.232.210.47:5006", // 示例
  targetF: "http://132.232.210.47:5004",
  targetG: "http://132.232.210.47:5005", // 【新增】离线推荐服务
};

export { devProxy, prodProxy, ZHJProxy };