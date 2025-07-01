import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

export const useUserStore = defineStore('user', () => {
    // 1. --- STATE ---
    // 从 localStorage 初始化 state，这样即使用户刷新页面，登录状态也能保持
    const user = ref(JSON.parse(localStorage.getItem('user_profile')) || null);
    const token = ref(localStorage.getItem('auth_token') || null);
    const sessionId = ref(localStorage.getItem('session_id') || null);

    // 2. --- GETTERS ---
    // Getter 用于派生 state，方便在组件中使用
    const isLoggedIn = computed(() => !!token.value && !!user.value);
    
    // 创建一个 Getter 来生成认证头，这在调用需要授权的 API 时非常有用
    const authHeader = computed(() => {
        return { headers: { Authorization: `Bearer ${token.value}` } };
    });

    // 3. --- ACTIONS ---
    /**
     * 设置用户和 Token，并持久化到 localStorage
     * 这是一个内部辅助函数
     * @param {object} userData - 用户信息对象
     * @param {string} userToken - 认证 Token
     */
    function setUserAndToken(userData, userToken) {
        user.value = userData;
        token.value = userToken;
        localStorage.setItem('user_profile', JSON.stringify(userData));
        localStorage.setItem('auth_token', userToken);

        // 创建并存储一个新的会话 ID
        const newSessionId = uuidv4();
        sessionId.value = newSessionId;
        localStorage.setItem('session_id', newSessionId);
    }

    /**
     * 登录 Action
     * @param {object} credentials - 包含 username 和 password 的对象
     */
    async function login(credentials) {
        // 后端登录接口地址
        const endpoint = '/service-a/api/auth/login';
        
        const response = await axios.post(endpoint, credentials);

        // 假设后端成功后返回的数据结构如你组件中所示
        const { user_id, token, nickname, email, avatar_url } = response.data;
        if (user_id && token) {
            const userData = {
                id: user_id,
                nickname: nickname || credentials.username,
                email: email || '',
                avatar_url: avatar_url || 'https://via.placeholder.com/150'
            };
            setUserAndToken(userData, token);
        } else {
            // 如果成功响应中缺少关键信息，则抛出错误
            throw new Error('Login response missing token or user_id');
        }
        return response.data; // 返回完整数据，以便组件可以显示成功消息
    }

    /**
     * 注册 Action
     * @param {object} details - 包含 username, email, password 的对象
     */
    async function register(details) {
        const endpoint = '/service-a/api/auth/register';
        const response = await axios.post(endpoint, details);
        return response.data; // 直接返回后端响应
    }

    /**
     * 登出 Action
     */
    function logout() {
        user.value = null;
        token.value = null;
        sessionId.value = null;
        localStorage.removeItem('user_profile');
        localStorage.removeItem('auth_token');
        localStorage.removeItem('session_id');
        // 可选：登出后跳转到登录页，这可以在组件中完成，也可以在这里触发
    }

    // 暴露 state, getters, 和 actions
    return {
        user,
        token,
        isLoggedIn,
        authHeader,
        login,
        register,
        logout,
    };
});