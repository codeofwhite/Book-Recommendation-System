// config.js
const devProxy = {
  targetA: "http://localhost:5000",
  targetB: "http://localhost:5001",
};

const prodProxy = {
  targetA: "http://132.232.210.47:5000",
  targetB: "http://132.232.210.47:5001",
};

export { devProxy, prodProxy };