<template>
  <div class="onboarding-container">
    <h2>完善您的个人资料</h2>
    <p>为了给您提供更精准的图书推荐，请填写以下信息。</p>

    <form @submit.prevent="submitProfile">
      <div class="form-group">
        <label for="age">年龄:</label>
        <input type="number" id="age" v-model.number="profile.age" min="0" max="120" placeholder="您的年龄" />
      </div>

      <div class="form-group">
        <label for="gender">性别:</label>
        <select id="gender" v-model="profile.gender">
          <option value="">请选择</option>
          <option value="male">男</option>
          <option value="female">女</option>
          <option value="other">其他</option>
        </select>
      </div>

      <div class="form-group">
        <label for="location">所在地区:</label>
        <input type="text" id="location" v-model="profile.location" placeholder="例如：台北市" />
      </div>

      <div class="form-group">
        <label for="occupation">职业:</label>
        <input type="text" id="occupation" v-model="profile.occupation" placeholder="例如：学生、工程师" />
      </div>

      <div class="form-group">
        <label for="interest_tags">兴趣标签 (逗号分隔):</label>
        <input type="text" id="interest_tags" v-model="profile.interest_tags" placeholder="例如：历史,科幻,编程" />
      </div>

      <div class="form-group">
        <label>偏好图书类型:</label>
        <div>
          <label><input type="checkbox" value="fiction" v-model="preferredBookTypesArray"> 小说</label>
          <label><input type="checkbox" value="non-fiction" v-model="preferredBookTypesArray"> 非小说</label>
          <label><input type="checkbox" value="biography" v-model="preferredBookTypesArray"> 传记</label>
        </div>
      </div>

      <div class="form-group">
        <label for="preferred_authors">偏好作者 (逗号分隔):</label>
        <input type="text" id="preferred_authors" v-model="profile.preferred_authors" placeholder="例如：鲁迅,村上春树" />
      </div>

      <div class="form-group">
        <label for="preferred_genres">偏好题材 (逗号分隔):</label>
        <input type="text" id="preferred_genres" v-model="profile.preferred_genres" placeholder="例如：推理,奇幻,悬疑" />
      </div>

      <div class="form-group">
        <label>偏好阅读时长:</label>
        <div>
          <label><input type="radio" value="short" v-model="profile.preferred_reading_duration"> 短 (1小时内)</label>
          <label><input type="radio" value="medium" v-model="profile.preferred_reading_duration"> 中 (1-3小时)</label>
          <label><input type="radio" value="long" v-model="profile.preferred_reading_duration"> 长 (3小时以上)</label>
        </div>
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? '提交中...' : '提交问卷' }}
      </button>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="success" class="success-message">{{ success }}</p>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

// Helper function to get user data from localStorage
const getParsedUserData = () => {
  const storedUserData = localStorage.getItem('user_data');
  if (storedUserData) {
    try {
      return JSON.parse(storedUserData);
    } catch (e) {
      console.error("Error parsing user_data from localStorage:", e);
      return null;
    }
  }
  return null;
};

export default {
  name: 'UserOnboarding',
  data() {
    return {
      profile: {
        age: null,
        gender: '',
        location: '',
        occupation: '',
        interest_tags: '',
        preferred_authors: '',
        preferred_genres: '',
        preferred_reading_duration: '',
      },
      preferredBookTypesArray: [],
      loading: false,
      error: null,
      success: null,
      user_id: null,
    };
  },
  created() {
    const loggedInUser = getParsedUserData(); // 使用辅助函数
    if (loggedInUser && loggedInUser.user_id) {
      this.user_id = loggedInUser.user_id;
      this.fetchUserProfile();
    } else {
      console.warn("UserOnboarding: No user_id found in localStorage. Redirecting to login.");
      this.$router.push({ name: 'auth' });
    }
  },
  methods: {
    async fetchUserProfile() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`http://localhost:5000/api/users/${this.user_id}`);
        const userDataFromBackend = response.data; // 从后端获取的最新资料

        // 将获取到的数据填充到 profile
        this.profile.age = userDataFromBackend.age;
        this.profile.gender = userDataFromBackend.gender;
        this.profile.location = userDataFromBackend.location;
        this.profile.occupation = userDataFromBackend.occupation;
        this.profile.interest_tags = userDataFromBackend.interest_tags;
        this.preferredBookTypesArray = userDataFromBackend.preferred_book_types ? userDataFromBackend.preferred_book_types.split(',') : [];
        this.profile.preferred_authors = userDataFromBackend.preferred_authors;
        this.profile.preferred_genres = userDataFromBackend.preferred_genres;
        this.profile.preferred_reading_duration = userDataFromBackend.preferred_reading_duration;

        // **重要：更新 localStorage 中的 user_data，但保留 auth_token**
        const currentStoredUserData = getParsedUserData(); // 再次获取当前 localStorage 中的数据
        if (currentStoredUserData) {
          // 合并后端返回的资料，并保留 auth_token
          const updatedUserData = {
            ...currentStoredUserData, // 保留所有现有字段，包括 auth_token
            ...userDataFromBackend,   // 合并后端返回的最新资料
            // 确保 is_profile_complete 字段也被正确更新
            is_profile_complete: userDataFromBackend.is_profile_complete !== undefined ? userDataFromBackend.is_profile_complete : currentStoredUserData.is_profile_complete
          };
          localStorage.setItem('user_data', JSON.stringify(updatedUserData));
          console.log('UserOnboarding: fetchUserProfile updated localStorage with:', updatedUserData);
        }

      } catch (err) {
        console.error('Failed to fetch user profile:', err);
        this.error = '加载用户资料失败。';
        if (err.response && err.response.status === 401) {
          this.$router.push({ name: 'auth' });
        }
      } finally {
        this.loading = false;
      }
    },
    async submitProfile() {
      this.loading = true;
      this.error = null;
      this.success = null;

      try {
        this.profile.preferred_book_types = this.preferredBookTypesArray.join(',');

        const response = await axios.put(`http://localhost:5000/api/users/${this.user_id}/profile`, this.profile);

        this.success = response.data.message;

        // **核心修改：更新 localStorage 中的 'user_data' 对象，并保留 auth_token**
        const currentStoredUserData = getParsedUserData(); // 获取当前存储的完整用户数据
        if (currentStoredUserData) {
          // 合并提交的 profile 数据，并明确设置 is_profile_complete 为 true
          const updatedUserData = {
            ...currentStoredUserData, // 保留所有现有字段，包括 auth_token
            ...this.profile,          // 合并提交的问卷资料
            is_profile_complete: true // 问卷提交成功，标记为已完成
          };
          localStorage.setItem('user_data', JSON.stringify(updatedUserData));
          console.log('UserOnboarding: submitProfile updated localStorage with:', updatedUserData);
        }

        console.log("问卷提交成功，跳转到 /userview");
        this.$router.push({ name: 'UserView' });

      } catch (err) {
        console.error('Error submitting profile:', err);
        this.error = err.response?.data?.message || '提交失败，请稍后再试。';
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
/* 你的样式代码保持不变 */
.onboarding-container {
  max-width: 600px;
  margin: 50px auto;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  text-align: center;
}

.onboarding-container h2 {
  color: #333;
  margin-bottom: 20px;
}

.onboarding-container p {
  color: #666;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  /* 确保内边距和边框包含在宽度内 */
}

.form-group div label {
  display: inline-block;
  margin-right: 15px;
  font-weight: normal;
}

button {
  width: 100%;
  padding: 12px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover:not(:disabled) {
  background-color: #0056b3;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  margin-top: 10px;
}

.success-message {
  color: #28a745;
  margin-top: 10px;
}
</style>
