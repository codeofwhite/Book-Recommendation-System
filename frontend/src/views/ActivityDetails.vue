<template>
  <div class="activity-details-page">
    <p v-if="loading" class="loading-message">
      <div class="spinner"></div> 正在加载活动详情，请稍候...
    </p>

    <div v-else-if="activity" class="activity-content-wrapper">
      <button @click="router.back()" class="back-to-list-button">
        <i class="fas fa-arrow-left"></i> 返回活动列表
      </button>

      <div class="activity-header">
        <h1 class="activity-detail-title">{{ activity.title }}</h1>
        <p class="activity-subtitle">{{ activity.description }}</p>
      </div>

      <img :src="activity.image" :alt="activity.title" class="activity-detail-image" />

      <div class="activity-meta-grid">
        <div class="meta-item-card">
          <i class="fas fa-calendar-alt meta-icon"></i>
          <div class="meta-info">
            <strong>日期：</strong>
            <span>{{ activity.date }}</span>
          </div>
        </div>
        <div class="meta-item-card">
          <i class="fas fa-map-marker-alt meta-icon"></i>
          <div class="meta-info">
            <strong>地点：</strong>
            <span>{{ activity.location || (activity.type === 'online' ? '线上活动' : '待定') }}</span>
          </div>
        </div>
        <div class="meta-item-card">
          <i class="fas fa-tag meta-icon"></i>
          <div class="meta-info">
            <strong>类型：</strong>
            <span>{{ formatActivityType(activity.type) }}</span>
          </div>
        </div>
        <div class="meta-item-card">
          <i class="fas fa-info-circle meta-icon"></i>
          <div class="meta-info">
            <strong>状态：</strong>
            <span>{{ formatActivityStatus(activity.status) }}</span>
          </div>
        </div>
        <div v-if="activity.organizer" class="meta-item-card">
          <i class="fas fa-users meta-icon"></i>
          <div class="meta-info">
            <strong>主办方：</strong>
            <span>{{ activity.organizer }}</span>
          </div>
        </div>
      </div>

      <div class="activity-description-full">
        <h2>活动介绍</h2>
        <div class="description-content" v-html="formattedFullDescription"></div>
      </div>

      <div class="action-buttons-wrapper">
        <button v-if="activity.status === 'upcoming'" class="action-button primary" @click="handleJoinActivity">
          <i class="fas fa-clipboard-check"></i> 立即报名
        </button>
        <button v-else-if="activity.status === 'ended'" class="action-button secondary" disabled>
          <i class="fas fa-hourglass-end"></i> 活动已结束
        </button>
        <button v-else class="action-button secondary" disabled>
          <i class="fas fa-question-circle"></i> {{ formatActivityStatus(activity.status) }}
        </button>
      </div>

      <div class="related-content-section">
        </div>
    </div>

    <div v-else class="no-activity-found">
      <p>抱歉，未找到该活动详情。</p>
      <router-link to="/activities" class="back-link-bottom">返回活动列表</router-link>
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
/* 引入 Font Awesome 样式 */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

.activity-details-page {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: var(--color-background-card);
  border-radius: var(--border-radius-large);
  box-shadow: var(--shadow-medium);
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; /* 使用更现代的字体栈 */
  color: var(--color-text);
  line-height: 1.6;
}

/* 返回按钮 */
.back-to-list-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  margin-bottom: 2rem;
  background-color: var(--color-background-soft);
  color: var(--color-text-light);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-small);
  font-size: var(--font-size-medium);
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.back-to-list-button:hover {
  background-color: var(--color-hover);
  color: var(--color-heading);
  border-color: var(--color-primary);
}

.back-to-list-button .fas {
  font-size: 1rem;
}

/* 页面顶部标题和副标题 */
.activity-header {
  text-align: center;
  margin-bottom: 2rem;
}

.activity-detail-title {
  font-size: var(--font-size-hero-title); /* 保持大标题，但调整行高 */
  color: var(--color-heading);
  line-height: 1.2;
  margin-bottom: 0.8rem;
  font-weight: 700;
}

.activity-subtitle {
  font-size: var(--font-size-large);
  color: var(--color-text-light);
  max-width: 700px;
  margin: 0 auto;
  line-height: 1.5;
}

.activity-detail-image {
  width: 100%;
  max-height: 450px; /* 稍微增加图片高度 */
  object-fit: cover;
  border-radius: var(--border-radius-medium);
  margin-bottom: 3rem; /* 增加图片与下方信息的间距 */
  box-shadow: var(--shadow-medium); /* 提升阴影效果 */
}

/* 元信息网格布局 */
.activity-meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* 更灵活的列数 */
  gap: 1.5rem; /* 增加间距 */
  margin-bottom: 3rem;
  background-color: var(--color-background-soft); /* 保持背景色 */
  padding: 1.8rem; /* 增加内边距 */
  border-radius: var(--border-radius-large); /* 更大的圆角 */
  box-shadow: var(--shadow-small); /* 细微的阴影 */
}

.meta-item-card {
  display: flex;
  align-items: flex-start; /* 顶部对齐图标和文本 */
  gap: 1rem;
  font-size: var(--font-size-medium);
  color: var(--color-text);
  padding: 0.5rem; /* 微调内边距 */
  /* border-left: 3px solid var(--color-primary-light); /* 左侧强调线 */
}

.meta-icon {
  font-size: 1.8rem; /* 增大图标尺寸 */
  color: var(--color-primary); /* 使用主题色 */
  flex-shrink: 0; /* 防止图标被压缩 */
  margin-top: 0.2rem; /* 微调图标位置 */
}

.meta-info {
  display: flex;
  flex-direction: column; /* 标题和内容垂直排列 */
}

.meta-info strong {
  font-size: var(--font-size-medium); /* 加粗标题，保持大小 */
  color: var(--color-heading);
  margin-bottom: 0.2rem; /* 标题和内容间距 */
  font-weight: 600; /* 适度加粗 */
}

.meta-info span {
  font-size: var(--font-size-medium);
  color: var(--color-text);
}


/* 活动介绍部分 */
.activity-description-full {
  margin-bottom: 3rem;
  background-color: var(--color-background-soft);
  padding: 2rem;
  border-radius: var(--border-radius-large);
  box-shadow: var(--shadow-small);
}

.activity-description-full h2 {
  font-size: var(--font-size-title);
  color: var(--color-heading);
  margin-bottom: 1.5rem; /* 增大标题与内容间距 */
  border-bottom: 2px solid var(--color-border);
  padding-bottom: 0.8rem;
  font-weight: 700;
}

/* fullDescription 的富文本样式 */
.description-content p {
  font-size: var(--font-size-large); /* 增大正文行高和字体大小 */
  color: var(--color-text);
  margin-bottom: 1.2rem;
  line-height: 1.8; /* 增加行距 */
}

.description-content h3 {
  font-size: var(--font-size-title-small);
  color: var(--color-heading);
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.description-content ul,
.description-content ol {
  margin-left: 1.5rem;
  margin-bottom: 1.2rem;
  list-style-position: inside; /* 让列表标记在文本内部 */
}

.description-content ul li,
.description-content ol li {
  font-size: var(--font-size-medium);
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.description-content strong {
  color: var(--color-heading); /* 突出粗体文本 */
}

/* 报名按钮区域 */
.action-buttons-wrapper {
  text-align: center;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px dashed var(--color-border); /* 增加顶部虚线分隔 */
}

.action-button {
  padding: 1.2rem 2.5rem; /* 增大按钮内边距 */
  font-size: var(--font-size-large);
  border: none;
  border-radius: var(--border-radius-medium);
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.8rem; /* 增大图标和文字间距 */
  font-weight: 600;
  text-transform: uppercase; /* 按钮文字大写 */
  letter-spacing: 0.05em; /* 增加字母间距 */
}

.action-button .fas {
  font-size: 1.2rem; /* 增大按钮内图标尺寸 */
}

.action-button.primary {
  background-color: var(--color-primary);
  color: rgb(250, 0, 0);
  box-shadow: var(--shadow-button-primary); /* 增加按钮阴影 */
}

.action-button.primary:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-3px); /* 悬停时向上浮动 */
  box-shadow: var(--shadow-button-primary-hover);
}

.action-button.secondary {
  background-color: var(--color-background-mute);
  color: var(--color-text-light);
  cursor: not-allowed;
  opacity: 0.8; /* 禁用状态略微透明 */
}

.no-activity-found,
.loading-message {
  text-align: center;
  padding: 5rem; /* 增加内边距 */
  font-size: var(--font-size-large);
  color: var(--color-text-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  min-height: 400px; /* 确保有足够的显示高度 */
}

.back-link-bottom {
  display: inline-block;
  margin-top: 1.5rem;
  padding: 0.9rem 1.8rem;
  background-color: var(--color-primary);
  color: white;
  text-decoration: none;
  border-radius: var(--border-radius-small);
  transition: background-color 0.2s ease, transform 0.2s ease;
  font-weight: 500;
}

.back-link-bottom:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-2px);
}

/* Loading spinner styles */
.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: var(--color-primary);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .activity-details-page {
    padding: 1rem;
    margin: 1rem auto;
  }
  .activity-detail-title {
    font-size: var(--font-size-title);
  }
  .activity-subtitle {
    font-size: var(--font-size-medium);
  }
  .activity-detail-image {
    max-height: 250px;
    margin-bottom: 2rem;
  }
  .activity-meta-grid {
    grid-template-columns: 1fr; /* 小屏幕下堆叠显示 */
    padding: 1.2rem;
    gap: 1rem;
  }
  .meta-item-card {
    align-items: center; /* 图标和文本垂直居中 */
  }
  .meta-icon {
    font-size: 1.5rem;
    margin-top: 0;
  }
  .activity-description-full {
    padding: 1.5rem;
  }
  .activity-description-full h2 {
    font-size: var(--font-size-medium);
    margin-bottom: 1rem;
  }
  .description-content p,
  .description-content ul li,
  .description-content ol li {
    font-size: var(--font-size-medium);
  }
  .action-button {
    width: 100%;
    padding: 0.8rem 1.5rem;
    font-size: var(--font-size-medium);
  }
  .action-buttons-wrapper {
    padding-top: 1.5rem;
  }
}
</style>