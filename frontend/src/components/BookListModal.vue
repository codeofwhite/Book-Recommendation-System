<template>
  <transition name="slide-fade">
    <div v-if="isVisible" class="book-list-modal-overlay" @click.self="closeModal">
      <div class="book-list-modal-content">
        <div class="modal-header">
          <h2>{{ title }}</h2>
          <button class="close-button" @click="closeModal" aria-label="关闭弹窗">&#x2715;</button>
        </div>
        <div class="modal-body">
          <div v-if="books.length > 0" class="book-grid-modal">
            <div v-for="book in books" :key="book.id" class="book-card-modal">
              <img :src="book.coverImg" :alt="book.title" class="book-cover-modal" />
              <div class="book-info-modal">
                <h3 class="book-title-modal">{{ book.title }}</h3>
                <p class="book-author-modal">作者: {{ book.author }}</p>
                <p class="book-genre-modal" v-if="book.genres && book.genres.length > 0">分类: {{ book.genres[0] }}</p>
                <button @click="viewBookDetails(book.id)" class="details-button-modal">查看详情</button>
              </div>
            </div>
          </div>
          <p v-else class="no-books-message">暂无相关书籍。</p>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '书籍列表',
  },
  books: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(['close', 'view-details']);

const router = useRouter();

const closeModal = () => {
  emit('close');
};

const viewBookDetails = (bookId) => {
  emit('close');
  router.push(`/books/${bookId}`);
};
</script>

<style scoped>
/* 字体和颜色变量 - 已调整为亮色系 */
:root {
  --modal-bg-color: #FFFFFF; /* 弹窗背景色，白色 */
  --modal-header-bg: #F8F9FA; /* 弹窗头部背景，浅灰色 */
  --modal-text-color: #495057; /* 主要文本颜色，深灰色 */
  --modal-heading-color: #212529; /* 标题颜色，更深的灰色 */
  --modal-border-color: #E9ECEF; /* 边框颜色，浅浅的灰色 */
  --modal-accent-color: #007BFF; /* 主题强调色，蓝色 */
  --modal-accent-hover: #0056b3; /* 主题强调色悬停，更深的蓝色 */
  --modal-shadow-color: rgba(0, 0, 0, 0.1); /* 阴影颜色，更淡 */
  --modal-card-bg: #FFFFFF; /* 卡片背景，白色 */
  --font-primary: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-secondary: 'Georgia', 'Times New Roman', serif;
}

/* 基础重置 */
* {
  box-sizing: border-box;
}

/* 弹窗遮罩层 */
.book-list-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4); /* 遮罩层略微变浅 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

/* 弹窗内容容器 */
.book-list-modal-content {
  background-color: var(--modal-bg-color);
  border-radius: 12px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 10px 30px var(--modal-shadow-color);
  font-family: var(--font-primary);
}

/* 弹窗头部 */
.modal-header {
  padding: 20px 25px;
  border-bottom: 1px solid var(--modal-border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--modal-header-bg);
  position: relative;
}

.modal-header h2 {
  margin: 0;
  color: var(--modal-heading-color);
  font-size: 1.8rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* 关闭按钮 */
.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  color: #6C757D; /* 关闭按钮颜色调整 */
  cursor: pointer;
  padding: 5px;
  line-height: 1;
  transition: all 0.2s ease;
}

.close-button:hover {
  color: var(--modal-accent-color);
  transform: scale(1.1);
}

/* 弹窗主体内容 */
.modal-body {
  flex: 1;
  padding: 25px;
  overflow-y: auto;
  background-color: var(--modal-bg-color);
}

/* 书籍网格布局 */
.book-grid-modal {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 25px;
  justify-items: center;
}

/* 书籍卡片 */
.book-card-modal {
  background: var(--modal-card-bg);
  border-radius: 8px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05); /* 卡片阴影更淡 */
  overflow: hidden;
  display: flex;
  flex-direction: column;
  width: 100%;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid var(--modal-border-color);
}

.book-card-modal:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1); /* 悬停阴影更淡 */
}

/* 书籍封面 */
.book-cover-modal {
  width: 100%;
  height: 240px;
  object-fit: cover;
  border-bottom: 1px solid var(--modal-border-color);
}

/* 书籍信息 */
.book-info-modal {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.book-title-modal {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--modal-heading-color);
  margin: 0;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.book-author-modal, .book-genre-modal {
  font-size: 0.95rem;
  color: var(--modal-text-color);
  margin: 0;
  line-height: 1.5;
}

/* 详情按钮 */
.details-button-modal {
  background-color: var(--modal-accent-color);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 15px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: background-color 0.3s ease;
  margin-top: 10px;
  width: 100%;
}

.details-button-modal:hover {
  background-color: var(--modal-accent-hover);
}

/* 无书籍提示 */
.no-books-message {
  text-align: center;
  color: var(--modal-text-color);
  font-size: 1.1rem;
  padding: 40px 20px;
  font-family: var(--font-secondary);
}

/* 过渡动画 */
.slide-fade-enter-active, .slide-fade-leave-active {
  transition: all 0.3s ease-out;
}

.slide-fade-enter-from, .slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-30px) scale(0.98);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .book-list-modal-content {
    width: 95%;
    max-height: 95vh;
  }
  
  .modal-header h2 {
    font-size: 1.5rem;
  }
  
  .book-grid-modal {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
  
  .book-cover-modal {
    height: 200px;
  }
}

@media (max-width: 480px) {
  .book-grid-modal {
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 12px;
  }
  
  .book-cover-modal {
    height: 180px;
  }
  
  .book-info-modal {
    padding: 12px;
  }
  
  .book-title-modal {
    font-size: 1rem;
  }
  
  .book-author-modal, .book-genre-modal {
    font-size: 0.85rem;
  }
  
  .details-button-modal {
    padding: 8px 12px;
    font-size: 0.85rem;
  }
}
</style>