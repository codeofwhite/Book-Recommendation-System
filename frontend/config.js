// config.js
const devProxy = {
  targetA: "http://localhost:5000",
  targetB: "http://localhost:5001",
  targetC: "http://localhost:5003",
  targetD: "http://localhost:5002", // 新增 5002 端口
};

const ZHJProxy = {
  targetA: "http://10.242.30.147:5000",
  targetB: "http://10.242.30.147:5001",
  targetC: "http://10.242.30.147:5003",
  targetD: "http://10.242.30.147:5002", // 新增 5002 端口
};

const prodProxy = {
  targetA: "http://132.232.210.47:5000",
  targetB: "http://132.232.210.47:5001",
  targetC: "http://132.232.210.47:5003",
  targetD: "http://132.232.210.47:5002", // 新增 5002 端口
};

export { devProxy, prodProxy, ZHJProxy };