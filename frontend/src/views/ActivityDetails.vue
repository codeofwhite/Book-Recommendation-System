<template>
  <div class="activity-details-page">
    <div v-if="loading" class="loading-state">
      <div class="custom-spinner"></div>
      <p>正在为您呈上雅集详情...</p>
    </div>

    <div v-else-if="activity" class="activity-container">
      <nav class="detail-nav">
        <button @click="router.back()" class="back-btn">
          <span class="icon">⇠</span> 返回列表
        </button>
        <div class="nav-share">
          <span class="badge" :class="activity.type">{{ formatActivityType(activity.type) }}</span>
        </div>
      </nav>

      <header class="activity-hero">
        <div class="hero-text">
          <h1 class="activity-title">{{ activity.title }}</h1>
          <p class="activity-intro">{{ activity.description }}</p>
        </div>
        <div class="image-frame">
          <img :src="activity.image" :alt="activity.title" class="hero-image" />
          <div class="image-decoration"></div>
        </div>
      </header>

      <div class="content-layout">
        <main class="main-content">
          <section class="description-section">
            <h2 class="section-label"><span>雅集详情</span></h2>
            <div class="rich-text-content" v-html="formattedFullDescription"></div>
          </section>
        </main>

        <aside class="info-sidebar">
          <div class="sticky-card">
            <div class="info-grid">
              <div class="info-item">
                <div class="info-icon">📅</div>
                <div class="info-body">
                  <label>活动时间</label>
                  <span>{{ activity.date }}</span>
                </div>
              </div>
              <div class="info-item">
                <div class="info-icon">📍</div>
                <div class="info-body">
                  <label>雅集地点</label>
                  <span>{{ activity.location || '线上雅集' }}</span>
                </div>
              </div>
              <div class="info-item">
                <div class="info-icon">🏛️</div>
                <div class="info-body">
                  <label>主办方</label>
                  <span>{{ activity.organizer }}</span>
                </div>
              </div>
              <div class="info-item">
                <div class="info-icon">⏳</div>
                <div class="info-body">
                  <label>当前状态</label>
                  <span class="status-text">{{ formatActivityStatus(activity.status) }}</span>
                </div>
              </div>
            </div>

            <div class="action-zone">
              <button 
                v-if="activity.status === 'upcoming'" 
                class="join-btn" 
                @click="handleJoinActivity"
              >
                立即预约席位
              </button>
              <button v-else class="join-btn disabled" disabled>
                {{ formatActivityStatus(activity.status) }}
              </button>
              <p class="join-note" v-if="activity.status === 'upcoming'">* 预约成功后，我们将通过邮件发送回执</p>
            </div>
          </div>
        </aside>
      </div>
    </div>

    <div v-else class="error-state">
      <div class="error-icon">🍂</div>
      <h2>雅集信息已逸散</h2>
      <p>抱歉，未找到该活动的详细记载</p>
      <button @click="router.push('/activities')" class="back-link">寻找其他雅集</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'; // 导入 computed
import { useRoute, useRouter } from 'vue-router';
// import axios from 'axios'; // 未来用于从后端获取数据时启用

const route = useRoute();
const router = useRouter();
const activity = ref(null);
const loading = ref(true);

// 模拟的活动数据，与 ActivitiesPage 中的 mockActivities 对应
const mockActivities = [
  {
    id: 'a1',
    title: '夏日读书挑战赛：奇幻文学专题',
    date: '2025年7月1日 - 8月31日',
    location: '线上，活动平台：Discord',
    image: 'https://th.bing.com/th/id/OIP.z8K89wSx6Od2ctAjgdEE5gHaEM?w=310&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3',
    description: '深入奇幻文学的瑰丽世界，挑战阅读极限，赢取丰厚奖励，与书友共度精彩夏日。',
    fullDescription: `
      <p>这是一个为期两个月的线上读书挑战赛，旨在鼓励读者探索奇幻文学的魅力。参与者需在活动期间阅读指定或自选的奇幻类书籍，并提交读书笔记或评论。</p>
      <p>活动结束时，将根据阅读量和参与度评选出优胜者，并颁发丰厚奖品，包括限量版书籍、电子阅读器和平台会员资格。活动期间还将不定期举办线上交流会。</p>
      <h3>活动日程安排</h3>
      <ul>
        <li><strong>第一周：</strong> 奇幻文学入门与导读</li>
        <li><strong>第二至四周：</strong> 自由阅读与线上讨论</li>
        <li><strong>第五周：</strong> 主题分享会：我最喜爱的奇幻角色</li>
        <li><strong>第六至八周：</strong> 深入阅读与创作实践</li>
        <li><strong>活动结束：</strong> 颁奖典礼与总结分享</li>
      </ul>
      <p>期待您的加入，共同开启奇幻阅读之旅！</p>
    `, // fullDescription 可以包含 HTML
    type: 'challenge',
    status: 'upcoming',
    organizer: '知识宏大挂毯平台'
  },
  {
    id: 'a2',
    title: '线上读书分享会：哲学思辨之夜',
    date: '2025年7月15日 19:00 - 21:00 (CST)',
    location: '线上，会议链接将在报名成功后发送',
    image: 'https://th.bing.com/th/id/OIP.ac8a6uFFGWNUWltXnKib4AHaQY?w=158&h=349&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3',
    description: '邀请知名哲学家，共同探讨人生、宇宙与存在的意义，线上互动交流。',
    fullDescription: `
      <p>本次分享会将邀请著名哲学学者李教授，围绕“后现代语境下的个体意义构建”展开深入探讨。李教授将从康德、尼采等哲学巨匠的思想到当代社会思潮，深入浅出地阐述个体如何在复杂世界中寻找并确立自身价值。</p>
      <p>参与者可以在线上提问，与教授和其他书友进行思辨交流。我们鼓励大家带着自己的疑问和思考前来，共同碰撞思想的火花。适合对哲学有兴趣的初学者和资深爱好者。</p>
      <p><strong>主讲嘉宾：</strong> 李教授，知名哲学系教授，著有多本哲学普及著作。</p>
      <p>活动将全程录像，并在会后提供回放链接。请务必提前报名，以便我们发送会议链接和相关资料。</p>
    `,
    type: 'online',
    status: 'upcoming',
    organizer: '思辨沙龙'
  },
  {
    id: 'a3',
    title: '线下作家见面会：历史长河探秘',
    date: '2025年7月20日 14:00 - 16:00 (CST)',
    location: '台北市大安区书店街123号',
    image: 'https://th.bing.com/th/id/OIP.j2QL_B60LLgWU7x-xH6b6gHaHa?w=192&h=193&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3',
    description: '与畅销历史作家面对面，分享创作故事和历史发现的乐趣，现场签售。',
    fullDescription: `
      <p>我们非常荣幸邀请到历史畅销书作家王老师，举办一场“历史长河探秘”主题分享会。王老师将分享他创作《盛世浮沉》背后的故事，以及如何从浩瀚史料中挖掘趣味细节。</p>
      <p>此次活动是近距离接触王老师，了解其创作灵感和方法论的绝佳机会。现场设有互动问答环节和签售会，是历史爱好者不容错过的盛会。</p>
      <h3>活动流程：</h3>
      <ol>
        <li>作家分享：从历史中汲取灵感</li>
        <li>互动问答：现场提问与交流</li>
        <li>签名售书：与王老师合影留念</li>
      </ol>
      <p>数量有限，请提前报名，以确保您的席位。</p>
    `,
    type: 'offline',
    status: 'upcoming',
    organizer: '城市文化书店'
  },
  {
    id: 'a4',
    title: '青年创作者工作坊：故事构建技巧',
    date: '2025年8月5日 19:30 - 21:00 (CST)',
    location: '线上，腾讯会议室',
    image: 'https://th.bing.com/th/id/OIP.w4PWaTPnW8Z79qSTqPk0xwHaC9?w=322&h=139&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3',
    description: '针对青年作家，提升故事构思、人物塑造和情节发展能力。',
    fullDescription: `
      <p>本次工作坊由资深编辑和畅销书作家共同指导，旨在帮助有志于写作的青年提升故事构建的核心技巧。课程内容包括：</p>
      <ul>
        <li>如何提炼故事核心</li>
        <li>人物弧光设计</li>
        <li>多线叙事布局</li>
        <li>冲突与高潮的设置</li>
      </ul>
      <p>通过案例分析和现场练习，让学员快速掌握创作要领。无论你是文学爱好者还是初出茅庐的创作者，都能在这里找到提升的路径。</p>
      <p><strong>导师：</strong> XXX编辑，YYY畅销书作家。</p>
      <p>名额有限，报名从速！</p>
    `,
    type: 'online',
    status: 'upcoming',
    organizer: '文学创作中心'
  },
];

onMounted(() => {
  loading.value = true;
  const activityId = route.params.id; // 从路由参数获取活动ID
  setTimeout(() => {
    // 模拟从 mockActivities 中查找对应ID的活动
    const foundActivity = mockActivities.find(a => a.id === activityId);
    if (foundActivity) {
      activity.value = foundActivity;
    }
    loading.value = false;
  }, 300); // 模拟网络请求延迟
});

const handleJoinActivity = () => {
  const loggedInUser = localStorage.getItem('user_data');
  if (!loggedInUser) {
    alert('请先登录才能报名活动！');
    router.push({ name: 'auth' }); // 跳转到登录页
    return;
  }
  alert(`您已成功报名：《${activity.value.title}》！我们会在活动开始前通过邮件通知您。`);
  console.log(`用户 ${loggedInUser} 报名了活动 ${activity.value.title}`);
};

const formatActivityType = (type) => {
  switch (type) {
    case 'online': return '线上活动';
    case 'offline': return '线下活动';
    case 'challenge': return '挑战赛';
    default: return '其他';
  }
};

const formatActivityStatus = (status) => {
  switch (status) {
    case 'upcoming': return '即将开始';
    case 'ongoing': return '进行中';
    case 'ended': return '已结束';
    case 'cancelled': return '已取消';
    default: return '未知状态';
  }
};

// 计算属性，用于渲染包含HTML的fullDescription
const formattedFullDescription = computed(() => {
  return activity.value?.fullDescription || activity.value?.description || '';
});
</script>

<style scoped>
.activity-details-page {
  --ink: #3A2E26;
  --wood: #8B6B4D;
  --paper: #FDFBFA;
  --accent-light: #F4EEE7;
  --font-serif: 'Noto Serif SC', serif;
  
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 80vh;
}

/* 导航 */
.detail-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.back-btn {
  background: none;
  border: none;
  color: var(--wood);
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.2s ease;
}

.back-btn:hover { transform: translateX(-5px); }

/* 头部设计 */
.activity-hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
  margin-bottom: 60px;
}

.activity-title {
  font-family: var(--font-serif);
  font-size: 2.8rem;
  color: var(--ink);
  line-height: 1.2;
  margin-bottom: 20px;
}

.activity-intro {
  font-size: 1.2rem;
  color: #665a52;
  line-height: 1.6;
}

.image-frame {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.hero-image {
  width: 100%;
  display: block;
  transition: transform 0.5s ease;
}

.image-decoration {
  position: absolute;
  inset: 0;
  border: 1px solid rgba(255,255,255,0.2);
  margin: 15px;
  pointer-events: none;
}

/* 布局控制 */
.content-layout {
  display: grid;
  grid-template-columns: 1.8fr 1fr;
  gap: 60px;
}

/* 正文内容 */
.section-label {
  font-family: var(--font-serif);
  font-size: 1.8rem;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.section-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--accent-light);
}

.rich-text-content :deep(p) {
  font-size: 1.1rem;
  line-height: 1.8;
  margin-bottom: 20px;
  color: var(--ink);
}

.rich-text-content :deep(h3) {
  font-family: var(--font-serif);
  font-size: 1.5rem;
  margin: 40px 0 20px;
  color: var(--wood);
}

/* 侧边信息栏 */
.sticky-card {
  position: sticky;
  top: 40px;
  background: white;
  padding: 30px;
  border-radius: 24px;
  border: 1px solid var(--accent-light);
  box-shadow: 0 10px 30px rgba(58, 46, 38, 0.05);
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 25px;
  margin-bottom: 35px;
}

.info-item {
  display: flex;
  gap: 15px;
}

.info-icon {
  font-size: 1.5rem;
  background: var(--accent-light);
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 12px;
}

.info-body label {
  display: block;
  font-size: 0.8rem;
  color: var(--wood);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 4px;
}

.info-body span {
  font-weight: 600;
  color: var(--ink);
}

/* 报名按钮 */
.join-btn {
  width: 100%;
  padding: 16px;
  border-radius: 14px;
  border: none;
  background: var(--wood);
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 20px rgba(139, 107, 77, 0.3);
}

.join-btn:hover {
  background: var(--ink);
  transform: translateY(-2px);
  box-shadow: 0 12px 25px rgba(58, 46, 38, 0.4);
}

.join-btn.disabled {
  background: #d1cbc5;
  box-shadow: none;
  cursor: not-allowed;
}

.join-note {
  font-size: 0.8rem;
  color: var(--wood);
  text-align: center;
  margin-top: 15px;
  opacity: 0.8;
}

/* 响应式 */
@media (max-width: 900px) {
  .activity-hero { grid-template-columns: 1fr; gap: 30px; }
  .content-layout { grid-template-columns: 1fr; }
  .info-sidebar { order: -1; } /* 移动端信息栏在前 */
  .activity-title { font-size: 2.2rem; }
}

/* 装饰性样式 */
.badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}
.badge.challenge { background: #FDEBD0; color: #E67E22; }
.badge.online { background: #EBF5FB; color: #3498DB; }
.badge.offline { background: #EAFAF1; color: #27AE60; }

.loading-state, .error-state {
  text-align: center;
  padding: 100px 0;
}
</style>