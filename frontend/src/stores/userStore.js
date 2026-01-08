import { defineStore } from "pinia";
import { ref, computed } from "vue";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";

export const useUserStore = defineStore("user", () => {
    // 1. --- STATE ---
    const user = ref(JSON.parse(localStorage.getItem("user_data")) || null);
    const token = ref(localStorage.getItem("auth_token") || null);
    const sessionId = ref(localStorage.getItem("session_id") || null);

    // 2. --- GETTERS ---
    const isLoggedIn = computed(() => !!token.value && !!user.value);
    const authHeader = computed(() => {
        return { headers: { Authorization: `Bearer ${token.value}` } };
    });

    // 3. --- ACTIONS ---
    function setUserAndToken(userData, userToken) {
        user.value = userData;
        token.value = userToken;
        localStorage.setItem("user_data", JSON.stringify(userData));
        localStorage.setItem("auth_token", userToken);

        const newSessionId = uuidv4();
        sessionId.value = newSessionId;
        localStorage.setItem("session_id", newSessionId);
    }

    /**
     * 登录 Action
     * @param {object} credentials - 包含 username 和 password 的对象
     */
    async function login(credentials) {
        // <-- 确保这是唯一的 login 函数
        const endpoint = "/service-a/api/auth/login";
        const response = await axios.post(endpoint, credentials);

        const {
            user_id,
            token,
            nickname,
            email,
            avatar_url,
            registration_date,
            last_login_date,
            age,
            gender,
            location,
            occupation,
            interest_tags,
            preferred_book_types,
            preferred_authors,
            preferred_genres,
            preferred_reading_duration,
            is_profile_complete,
        } = response.data;

        if (user_id && token) {
            const userDataToStore = {
                user_id: user_id,
                auth_token: token,
                nickname: nickname || credentials.username,
                email: email || "",
                avatar_url:
                    avatar_url ||
                    "https://th.bing.com/th/id/OIP.cTPVthB0oT1RXrEcSHaaTwHaHa?w=191&h=191&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3",
                registration_date: registration_date || null,
                last_login_date: last_login_date || null,
                age: age || null,
                gender: gender || "",
                location: location || "",
                occupation: occupation || "",
                interest_tags: interest_tags || "",
                preferred_book_types: preferred_book_types || "",
                preferred_authors: preferred_authors || "",
                preferred_genres: preferred_genres || "",
                preferred_reading_duration: preferred_reading_duration || "",
                is_profile_complete:
                    is_profile_complete === undefined ? false : is_profile_complete,
            };
            setUserAndToken(userDataToStore, token);
        } else {
            throw new Error("Login response missing token or user_id");
        }
        return response.data;
    }

    async function register(details) {
        const endpoint = "/service-a/api/auth/register";
        const response = await axios.post(endpoint, details);
        return response.data;
    }

    function logout() {
        user.value = null;
        token.value = null;
        sessionId.value = null;
        // 移除所有相关的 localStorage 项，包括 'user_data'
        localStorage.removeItem("user_data"); // <-- 确保这里是 'user_data'
        localStorage.removeItem("auth_token");
        localStorage.removeItem("session_id");
    }

    return {
        user,
        token,
        sessionId,
        isLoggedIn,
        authHeader,
        login,
        register,
        logout,
    };
});
