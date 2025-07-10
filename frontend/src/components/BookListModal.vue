<template>
  <transition name="fade-scale">
    <div v-if="isVisible" class="book-list-modal-overlay" @click.self="closeModal">
      <div class="book-list-modal-content">
        <div class="modal-header">
          <h2>{{ title }}</h2>
          <button class="close-button" @click="closeModal" aria-label="关闭弹窗">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              <path d="M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div v-if="books.length > 0" class="book-grid-modal">
            <div v-for="book in books" :key="book.id" class="book-card-modal">
              <div class="book-frame">
                <div class="book-cover-container">
                  <img :src="book.coverImg" :alt="book.title" class="book-cover-modal" />
                </div>
                <div class="book-spine"></div>
                <div class="book-bottom"></div>
              </div>
              <div class="book-info-modal">
                <h3 class="book-title-modal">{{ book.title }}</h3>
                <p class="book-author-modal">{{ book.author }}</p>
                <p class="book-genre-modal" v-if="book.genres && book.genres.length > 0">{{ book.genres[0] }}</p>
                <button @click="viewBookDetails(book.id)" class="details-button-modal">
                  <span>查看详情</span>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                    <path d="M12 5L19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="no-books-container">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M19 5V19H5V5H19ZM19 5H21V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V5C3 3.89543 3.89543 3 5 3H19C20.1046 3 21 3.89543 21 5V5Z"
                stroke="currentColor" stroke-width="2" />
              <path d="M12 7V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              <path d="M12 16.01L12.01 15.9989" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
            <p class="no-books-message">暂无相关书籍</p>
          </div>
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
/* 典雅配色方案 - 调整透明度 */
:root {
  --modal-bg-color: rgba(249, 245, 240, 0.95);
  /* 米白色背景，略微透明 */
  --modal-header-bg: rgba(240, 230, 214, 0.9);
  /* 浅米色头部，略微透明 */
  --modal-text-color: #5A4A42;
  /* 深棕色文字 */
  --modal-heading-color: #3A2E26;
  /* 更深棕色标题 */
  --modal-border-color: rgba(216, 196, 176, 0.8);
  /* 浅米色边框，略微透明 */
  --modal-accent-color: #8B6B4D;
  /* 棕色强调色 */
  --modal-accent-hover: #6B4F36;
  /* 深棕色悬停 */
  --modal-shadow-color: rgba(58, 46, 38, 0.15);
  /* 浅棕色阴影 */
  --modal-card-bg: rgba(255, 255, 255, 0.9);
  /* 白色卡片背景，略微透明 */
  --book-frame-color: rgba(224, 213, 200, 0.85);
  /* 书框颜色，略微透明 */
  --book-spine-color: rgba(211, 197, 179, 0.85);
  /* 书脊颜色，略微透明 */
  --scrollbar-thumb: rgba(184, 169, 154, 0.7);
  /* 滚动条滑块颜色，略微透明 */
  --scrollbar-track: rgba(237, 229, 220, 0.5);
  /* 滚动条轨道颜色，半透明 */
  --font-primary: 'Noto Serif SC', 'SimSun', serif;
  /* 典雅衬线字体 */
  --font-secondary: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
}

/* 基础重置 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* 弹窗遮罩层 - 调整透明度 */
.book-list-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.85);
  /* 米色背景，调整为70%透明度 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  transition: all 0.3s ease;
}

/* 弹窗内容容器 */
.book-list-modal-content {
  background-color: var(--modal-bg-color);
  border-radius: 12px;
  width: 90%;
  max-width: 1100px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 12px 36px var(--modal-shadow-color);
  font-family: var(--font-primary);
  border: 1px solid var(--modal-border-color);
  transition: all 0.3s ease;
}

/* 弹窗头部 */
.modal-header {
  padding: 22px 30px;
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
  font-size: 2rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  font-family: var(--font-primary);
}

/* 关闭按钮 */
.close-button {
  background: none;
  border: none;
  color: var(--modal-text-color);
  cursor: pointer;
  padding: 6px;
  line-height: 1;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  width: 40px;
  height: 40px;
}

.close-button:hover {
  color: var(--modal-accent-hover);
  background-color: rgba(139, 107, 77, 0.1);
  transform: rotate(90deg);
}

.close-button svg {
  width: 22px;
  height: 22px;
}

/* 弹窗主体内容 - 增强滚动区域 */
.modal-body {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  background-color: var(--modal-bg-color);
  scrollbar-width: thin;
  scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
}

/* 书籍网格布局 - 统一尺寸 */
.book-grid-modal {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 30px;
  justify-items: stretch;
}

/* 书籍卡片 - 统一高度 */
.book-card-modal {
  background: var(--modal-card-bg);
  border-radius: 10px;
  box-shadow: 0 4px 12px var(--modal-shadow-color);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 520px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid var(--modal-border-color);
  position: relative;
}

.book-card-modal:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(58, 46, 38, 0.15);
}

/* 书框效果 - 固定尺寸 */
.book-frame {
  position: relative;
  width: 100%;
  height: 320px;
  background: var(--book-frame-color);
  padding: 12px;
  box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.book-cover-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.book-spine {
  position: absolute;
  left: 0;
  top: 12px;
  bottom: 12px;
  width: 8px;
  background: var(--book-spine-color);
  box-shadow: inset -2px 0 4px rgba(0, 0, 0, 0.1);
}

.book-bottom {
  position: absolute;
  left: 8px;
  right: 12px;
  bottom: 0;
  height: 8px;
  background: var(--book-frame-color);
  box-shadow: inset 0 -2px 4px rgba(0, 0, 0, 0.1);
}

/* 书籍封面 */
.book-cover-modal {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.book-card-modal:hover .book-cover-modal {
  transform: scale(1.05);
}

/* 书籍信息 - 固定高度和字体增大 */
.book-info-modal {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-grow: 1;
  min-height: 200px;
}

.book-title-modal {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--modal-heading-color);
  margin: 0;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 3.6em;
  font-family: var(--font-primary);
}

.book-author-modal,
.book-genre-modal {
  font-size: 1.1rem;
  color: var(--modal-text-color);
  margin: 0;
  line-height: 1.5;
  font-family: var(--font-secondary);
}

.book-genre-modal {
  font-style: italic;
  margin-bottom: auto;
}

/* 详情按钮 - 增大字体 */
.details-button-modal {
  background-color: var(--modal-accent-color);
  color: rgb(158, 35, 35);
  border: none;
  border-radius: 6px;
  padding: 12px 18px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-top: auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: var(--font-secondary);
}

.details-button-modal:hover {
  background-color: var(--modal-accent-hover);
  transform: translateY(-2px);
}

.details-button-modal svg {
  width: 18px;
  height: 18px;
  transition: transform 0.3s ease;
}

.details-button-modal:hover svg {
  transform: translateX(3px);
}

/* 无书籍提示 */
.no-books-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.no-books-message {
  color: var(--modal-text-color);
  font-size: 1.4rem;
  margin-top: 20px;
  font-family: var(--font-primary);
}

.no-books-container svg {
  color: var(--modal-text-color);
}

/* 过渡动画 */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* 自定义滚动条样式 */
.modal-body::-webkit-scrollbar {
  width: 10px;
}

.modal-body::-webkit-scrollbar-track {
  background: var(--scrollbar-track);
  border-radius: 5px;
}

.modal-body::-webkit-scrollbar-thumb {
  background-color: var(--scrollbar-thumb);
  border-radius: 5px;
  border: 2px solid var(--scrollbar-track);
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background-color: var(--modal-accent-color);
}

/* Firefox滚动条 */
@supports (scrollbar-color: red blue) {
  .modal-body {
    scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
    scrollbar-width: thin;
  }
}

/* 响应式设计 */
@media (max-width: 992px) {
  .book-grid-modal {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 25px;
  }

  .book-frame {
    height: 300px;
  }

  .book-card-modal {
    min-height: 500px;
  }
}

@media (max-width: 768px) {
  .book-list-modal-content {
    width: 95%;
    max-height: 95vh;
  }

  .modal-header h2 {
    font-size: 1.8rem;
  }

  .book-grid-modal {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 20px;
  }

  .book-frame {
    height: 280px;
  }

  .book-card-modal {
    min-height: 480px;
  }

  .book-title-modal {
    font-size: 1.2rem;
  }

  .book-author-modal,
  .book-genre-modal {
    font-size: 1rem;
  }

  .details-button-modal {
    font-size: 1rem;
    padding: 10px 16px;
  }
}

@media (max-width: 576px) {
  .book-grid-modal {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 16px;
  }

  .book-frame {
    height: 240px;
    padding: 10px;
  }

  .book-card-modal {
    min-height: 440px;
  }

  .book-info-modal {
    padding: 16px;
  }

  .book-title-modal {
    font-size: 1.1rem;
  }

  .book-author-modal,
  .book-genre-modal {
    font-size: 0.95rem;
  }

  .modal-header {
    padding: 18px 24px;
  }

  .modal-body {
    padding: 24px;
  }

  .no-books-message {
    font-size: 1.2rem;
  }

  .modal-body::-webkit-scrollbar {
    width: 6px;
  }
}
</style>