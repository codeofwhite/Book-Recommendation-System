<template>
  <div class="onboarding-container">
    <div class="form-wrapper">
      <header class="header">
        <div class="title-container">
          <span class="icon" aria-hidden="true">📖</span>
          <h1>BookHug</h1>
        </div>
        <h2>个人专属阅读档案</h2>
        <p class="subtitle">让我们了解您的阅读偏好，为您推荐最契合心灵的优质好书</p>
      </header>

      <form @submit.prevent="submitProfile">
        <section class="form-section" aria-labelledby="basic-info-title">
          <h3 class="section-title" id="basic-info-title"><span>基本信息</span></h3>
          <div class="form-row">
            <div class="form-group">
              <label for="age">年龄</label>
              <input type="number" id="age" v-model.number="profile.age" min="0" max="120" placeholder="请输入您的年龄" />
            </div>
            <div class="form-group">
              <label for="gender">性别</label>
              <select id="gender" v-model="profile.gender" required>
                <option disabled value="">请选择</option>
                <option value="male">男</option>
                <option value="female">女</option>
                <option value="other">其他</option>
              </select>
            </div>
          </div>
        </section>

        <section class="form-section" aria-labelledby="background-info-title">
          <h3 class="section-title" id="background-info-title"><span>背景信息</span></h3>
          <div class="form-group full-width">
            <label for="occupation">职业/身份</label>
            <input type="text" id="occupation" v-model="profile.occupation" placeholder="例如：学生、职员、自由职业者" />
          </div>
          <div class="form-group full-width">
            <label for="location">所在地区</label>
            <input type="text" id="location" v-model="profile.location" placeholder="例如：北京、上海、广州" />
          </div>
        </section>

        <section class="form-section" aria-labelledby="reading-preference-title">
          <h3 class="section-title" id="reading-preference-title"><span>阅读偏好</span></h3>
          <div class="form-group full-width">
            <label>偏好的书籍类型</label>
            <div class="checkbox-group" role="group" aria-labelledby="reading-preference-title">
              <label class="elegant-checkbox">
                <input type="checkbox" value="fiction" v-model="preferredBookTypesArray"> <span>文学小说</span>
              </label>
              <label class="elegant-checkbox">
                <input type="checkbox" value="non-fiction" v-model="preferredBookTypesArray"> <span>人文社科</span>
              </label>
              <label class="elegant-checkbox">
                <input type="checkbox" value="biography" v-model="preferredBookTypesArray"> <span>人物传记</span>
              </label>
              <label class="elegant-checkbox">
                <input type="checkbox" value="sci-tech" v-model="preferredBookTypesArray"> <span>科普科技</span>
              </label>
              <label class="elegant-checkbox">
                <input type="checkbox" value="lifestyle" v-model="preferredBookTypesArray"> <span>生活艺术</span>
              </label>
            </div>
          </div>

          <div class="form-group full-width">
            <label for="preferred_authors">喜爱的作家</label>
            <input type="text" id="preferred_authors" v-model="profile.preferred_authors"
              placeholder="例如：余华、东野圭吾、村上春树" />
          </div>

          <div class="form-group full-width">
            <label for="preferred_genres">偏好的题材/风格</label>
            <input type="text" id="preferred_genres" v-model="profile.preferred_genres"
              placeholder="例如：悬疑推理、科幻奇幻、治愈系、历史纪实" />
          </div>

          <div class="form-group full-width">
            <label>通常的阅读时长</label>
            <div class="radio-group" role="radiogroup" aria-label="通常的阅读时长">
              <label class="elegant-radio">
                <input type="radio" value="short" v-model="profile.preferred_reading_duration"> <span>短时 (1小时内)</span>
              </label>
              <label class="elegant-radio">
                <input type="radio" value="medium" v-model="profile.preferred_reading_duration"> <span>适中 (1-3小时)</span>
              </label>
              <label class="elegant-radio">
                <input type="radio" value="long" v-model="profile.preferred_reading_duration"> <span>沉浸 (3小时以上)</span>
              </label>
            </div>
          </div>
        </section>

        <section class="form-section" aria-labelledby="interests-title">
          <h3 class="section-title" id="interests-title"><span>兴趣与目标</span></h3>
          <div class="form-group full-width">
            <label for="interest_tags">感兴趣的图书主题</label>
            <input type="text" id="interest_tags" v-model="profile.interest_tags" placeholder="例如：心理成长、自我提升、职场技能、历史文化" />
          </div>
        </section>

        <div class="form-footer">
          <button type="submit" :disabled="loading" class="submit-btn">
            {{ loading ? '正在提交...' : '生成我的阅读档案' }}
            <span v-if="!loading" style="margin-left: 8px; font-size: 1.2em; line-height: 1;">📖</span>
          </button>
          <p v-if="error" class="message error">{{ error }}</p>
          <p v-if="success" class="message success">{{ success }}</p>
        </div>
      </form>
    </div>
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
        const response = await axios.get(`/service-a/api/users/${this.user_id}`);
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

        const response = await axios.put(`/service-a/api/users/${this.user_id}/profile`, this.profile);

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
/* Copied and adapted from the final HTML version */
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;1,400&display=swap');

.onboarding-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 15px;
  min-height: 100vh;
  background: #f8f4ec;
  font-family: 'Lora', 'Georgia', serif;
}

.form-wrapper {
  max-width: 800px;
  width: 100%;
  background: linear-gradient(145deg, #ede6d1, #d9ceb4);
  border-radius: 12px;
  padding: 40px 45px 50px;
  box-sizing: border-box;
  box-shadow:
    inset 0 0 40px #c5b88c88,
    0 15px 30px rgba(149, 134, 110, 0.3);
  position: relative;
  overflow: hidden;
}

@keyframes glowMove {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
}

.header {
  text-align: center;
  margin-bottom: 40px;
  border-bottom: 1px solid #d3cfa5;
  padding-bottom: 30px;
}

.title-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-bottom: 15px;
}

.title-container .icon {
  font-size: 3.3rem;
  color: #bfae50;
  text-shadow: 0 0 8px #d6ca73cc;
  filter: none;
  user-select: none;
  line-height: 1;
}

.title-container h1 {
  font-size: 3rem;
  font-weight: 700;
  letter-spacing: 2px;
  background: linear-gradient(270deg, #9c8a48, #b9a95e, #9c8a48);
  background-size: 400% 400%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: glowMove 8s ease-in-out infinite;
  margin: 0;
  user-select: none;
  text-shadow:
    0 0 4px rgba(120, 100, 30, 0.5),
    0 0 15px rgba(160, 145, 60, 0.4);
  line-height: 1;
}

.header h2 {
  font-size: 1.8rem;
  color: #8c7f54;
  font-weight: 500;
  margin: 0 0 10px 0;
  text-shadow: 0 0 6px #a4986d55;
}

.header p.subtitle {
  font-style: italic;
  color: #a89f82;
  margin: 0;
  font-size: 1.2rem;
  letter-spacing: 1.2px;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 600;
  color: #7a6f46;
  text-align: center;
  margin: 45px 0 30px;
  display: flex;
  align-items: center;
  white-space: nowrap;
  user-select: none;
}

.section-title::before,
.section-title::after {
  content: "";
  flex: 1;
  height: 2px;
  background-image: linear-gradient(to right, transparent, #b5ab7e88, transparent);
  filter: drop-shadow(0 0 1.2px #a99f6fac);
}

.section-title span {
  margin: 0 30px;
  text-shadow: 0 0 3px #c1b996cc;
}

.form-row {
  display: flex;
  gap: 28px;
  flex-wrap: wrap;
}

.form-group {
  flex: 1 1 45%;
  margin-bottom: 28px;
}

.form-group.full-width {
  flex-basis: 100%;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #7a6e4fdd;
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: 0.2px;
  text-shadow: 0 0 1.8px #7b714a99;
  cursor: pointer;
  user-select: none;
}

input[type="text"],
input[type="number"],
select {
  width: 100%;
  padding: 15px 22px;
  border: 2px solid #b3a574cc;
  border-radius: 8px;
  background-color: #fef9f1;
  font-family: 'Lora', serif;
  font-size: 1.1rem;
  color: #6b5e3b;
  box-shadow:
    inset 0 2px 6px #c9be8b88;
  transition: border-color 0.35s ease, box-shadow 0.35s ease;
  box-sizing: border-box;
}

input::placeholder {
  color: #b1a978bb;
  font-style: italic;
}

input:focus,
select:focus {
  outline: none;
  border-color: #f6e588;
  box-shadow:
    0 0 12px 3px #f6e588bb,
    inset 0 2px 12px 1px #f8f4b8cc;
}

select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23a09244' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 18px center;
  background-size: 1.3em;
  cursor: pointer;
}

.checkbox-group,
.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 18px 30px;
  padding-top: 6px;
}

.elegant-checkbox,
.elegant-radio {
  display: flex;
  align-items: center;
  font-size: 1.05rem;
  cursor: pointer;
  color: #6b5e3b;
  user-select: none;
  transition: color 0.3s ease;
}

.elegant-checkbox:hover,
.elegant-radio:hover {
  color: #4a3d2f;
}

.elegant-checkbox input,
.elegant-radio input {
  margin-right: 12px;
  width: 22px;
  height: 22px;
  border: 2px solid #acaa76;
  border-radius: 5px;
  appearance: none;
  cursor: pointer;
  position: relative;
  background-color: #fdf9e6;
  transition: all 0.3s ease;
  box-shadow: inset 0 1px 3px #cdc98f;
  flex-shrink: 0;
}

.elegant-radio input {
  border-radius: 50%;
}

.elegant-checkbox input:checked,
.elegant-radio input:checked {
  background: radial-gradient(circle at center, #fff9a9, #d1ca76);
  border-color: #e8dd7d;
  transform: scale(1.1);
  box-shadow:
    0 0 8px 1.2px #e8dd7daa,
    inset 0 0 6px 1px #fffca0cc;
}

.elegant-checkbox input:checked+span::after {
  content: '✔';
  position: absolute;
  top: 50%;
  left: 11px;
  /* Adjust to center inside the box */
  transform: translate(-50%, -50%);
  color: #6b602a;
  font-size: 18px;
  text-shadow: 0 0 3px #c0b352;
  user-select: none;
  pointer-events: none;
  /* Make sure it doesn't block clicks */
}

.elegant-radio input:checked+span::after {
  content: '';
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #6b602a;
  top: 50%;
  left: 11px;
  /* Adjust to center */
  transform: translate(-50%, -50%);
  box-shadow: 0 0 6px 1px #c0b352cc;
  pointer-events: none;
}

.elegant-checkbox span,
.elegant-radio span {
  position: relative;
  padding-left: 1.8em;
  /* Space for the custom checkbox/radio */
}

/* We must override the native checkmark/dot */
.elegant-checkbox input:checked::after,
.elegant-radio input:checked::after {
  content: none;
}


.form-footer {
  text-align: center;
  margin-top: 40px;
}

.submit-btn {
  background: linear-gradient(135deg, #dfd486, #b29e45);
  color: #433916;
  border: none;
  padding: 17px 55px;
  font-size: 1.3rem;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.4s ease;
  font-family: 'Lora', serif;
  box-shadow: 0 0 12px 0 #d7ce87aa;
  position: relative;
  overflow: hidden;
  user-select: none;
  z-index: 10;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.submit-btn::after {
  content: '';
  position: absolute;
  width: 120%;
  height: 120%;
  background: radial-gradient(circle at center, #faf7cfa0 0%, transparent 70%);
  top: 50%;
  left: 50%;
  pointer-events: none;
  transform: translate(-50%, -50%) scale(0);
  transition: transform 0.45s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 50%;
  z-index: -1;
}

.submit-btn:hover::after {
  transform: translate(-50%, -50%) scale(1);
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #f0eea9, #bdb34e);
  box-shadow: 0 0 22px 4px #dfd97fbb;
  transform: translateY(-3px);
}

.submit-btn:disabled {
  background: #c1bc88;
  cursor: not-allowed;
  box-shadow: none;
  color: #7b7833;
  transform: none;
}

.message {
  margin-top: 28px;
  font-size: 1.15rem;
  font-style: italic;
  text-align: center;
  user-select: none;
  min-height: 1.5em;
  line-height: 1.4em;
  filter: drop-shadow(0 0 1px #9c955f);
}

.message.error {
  color: #c76060;
  text-shadow: 0 0 4px #ad4b4b;
}

.message.success {
  color: #7e9d4a;
  text-shadow: 0 0 6px #91a657;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-group {
    flex-basis: 100%;
    margin-bottom: 25px;
  }

  .onboarding-container {
    padding: 20px 10px;
  }

  .form-wrapper {
    padding: 30px 25px 40px;
  }
}
</style>
