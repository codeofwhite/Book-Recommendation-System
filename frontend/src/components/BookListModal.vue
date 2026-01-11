<template>
  <transition name="modal-bounce">
    <div v-if="isVisible" class="book-list-modal-overlay" @click.self="closeModal">
      <div class="book-list-modal-content">
        <div class="modal-header">
          <div class="header-title-area">
            <span class="decoration-line"></span>
            <h2>{{ title }}</h2>
          </div>
          <button class="close-button" @click="closeModal" aria-label="关闭弹窗">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <div v-if="books.length > 0" class="book-grid-modal">
            <div v-for="book in books" :key="book.id" class="book-card-modal" @click="viewBookDetails(book.id)">
              <div class="book-visual-wrapper">
                <div class="book-frame">
                  <div class="book-cover-container">
                    <img :src="book.coverImg" :alt="book.title" class="book-cover-modal" loading="lazy" />
                    <div class="cover-shimmer"></div>
                  </div>
                  <div class="book-spine"></div>
                </div>
                <div class="book-shadow"></div>
              </div>

              <div class="book-info-modal">
                <div class="text-content">
                  <h3 class="book-title-modal">{{ book.title }}</h3>
                  <p class="book-author-modal"><span>BY</span> {{ book.author }}</p>
                  <div class="tag-row">
                    <span class="book-genre-tag" v-if="book.genres && book.genres.length > 0">
                      {{ book.genres[0] }}
                    </span>
                  </div>
                </div>

                <button class="details-button-modal">
                  <span>阅读详情</span>
                  <div class="button-arrow">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                      <path d="M5 12H19M19 12L13 6M19 12L13 18" stroke="currentColor" stroke-width="2.5"
                        stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <div v-else class="no-books-container">
            <div class="empty-illustration">
              <div class="circle-bg"></div>
              <span class="empty-icon">📖</span>
            </div>
            <p class="no-books-message">书架空空如也，去寻觅一些典籍吧</p>
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
/* 声明变量 */
.book-list-modal-overlay {
  --primary-accent: #8B6B4D;
  --primary-hover: #5A4A42;
  --text-main: #3A2E26;
  --text-muted: #8E7E74;
  --bg-parchment: #FDFBFA;
  --header-glass: rgba(244, 238, 231, 0.96);
  --card-shadow: 0 10px 25px -5px rgba(58, 46, 38, 0.1);
  --font-serif: 'Noto Serif SC', 'SimSun', serif;
}

/* 遮罩层：增加毛玻璃效果 */
.book-list-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(30, 25, 20, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  padding: 20px;
}

/* 弹窗主体 */
.book-list-modal-content {
  background: var(--bg-parchment);
  width: 100%;
  max-width: 1200px;
  height: 85vh;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

/* 头部：精致化设计 */
.modal-header {
  padding: 24px 40px;
  background: var(--header-glass);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(139, 107, 77, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
}

.header-title-area {
  display: flex;
  align-items: center;
  gap: 15px;
}

.decoration-line {
  width: 4px;
  height: 24px;
  background: var(--primary-accent);
  border-radius: 2px;
}

.modal-header h2 {
  font-family: var(--font-serif);
  font-size: 1.75rem;
  color: var(--text-main);
  margin: 0;
}

.close-button {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1.5px solid rgba(139, 107, 77, 0.15);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.close-button:hover {
  background: var(--primary-accent);
  color: white;
  transform: rotate(90deg);
  border-color: var(--primary-accent);
}

/* 主体内容网格 */
.modal-body {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.book-grid-modal {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 40px;
}

/* 书籍卡片 */
.book-card-modal {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

/* 视觉容器：处理书籍的3D感 */
.book-visual-wrapper {
  position: relative;
  padding-bottom: 20px;
  perspective: 1000px;
}

.book-frame {
  position: relative;
  height: 340px;
  border-radius: 4px 12px 12px 4px;
  overflow: hidden;
  transition: all 0.5s ease;
  transform-style: preserve-3d;
  box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.1);
}

.book-cover-container {
  width: 100%;
  height: 100%;
  background: #eee;
}

.book-cover-modal {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-shimmer {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(105deg, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.2) 50%, rgba(255, 255, 255, 0) 100%);
  pointer-events: none;
}

.book-spine {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 12px;
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: brightness(0.8);
  box-shadow: inset -2px 0 5px rgba(0, 0, 0, 0.2);
}

/* 悬停动画 */
.book-card-modal:hover .book-frame {
  transform: rotateY(-15deg) translateY(-10px);
  box-shadow: 15px 20px 30px rgba(58, 46, 38, 0.2);
}

/* 书籍信息区 */
.book-info-modal {
  padding: 15px 5px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.book-title-modal {
  font-family: var(--font-serif);
  font-size: 1.25rem;
  color: var(--text-main);
  margin-bottom: 8px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-author-modal {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.book-author-modal span {
  font-size: 0.7rem;
  opacity: 0.6;
  margin-right: 4px;
}

.tag-row {
  margin-bottom: 20px;
}

.book-genre-tag {
  font-size: 0.75rem;
  padding: 4px 12px;
  background: rgba(139, 107, 77, 0.08);
  color: var(--primary-accent);
  border-radius: 20px;
  border: 1px solid rgba(139, 107, 77, 0.15);
}

/* 按钮优化 */
.details-button-modal {
  margin-top: auto;
  background: transparent;
  border: 1px solid rgba(139, 107, 77, 0.3);
  padding: 12px 16px;
  border-radius: 12px;
  color: var(--primary-accent);
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.book-card-modal:hover .details-button-modal {
  background: var(--primary-accent);
  color: white;
}

.button-arrow {
  transition: transform 0.3s ease;
}

.book-card-modal:hover .button-arrow {
  transform: translateX(4px);
}

/* 空状态美化 */
.empty-illustration {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 24px;
  display: grid;
  place-items: center;
}

.circle-bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(139, 107, 77, 0.05);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.empty-icon {
  font-size: 50px;
  z-index: 1;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.2);
    opacity: 0.5;
  }

  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 进场动画 */
.modal-bounce-enter-active {
  animation: modal-in 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-bounce-leave-active {
  animation: modal-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) reverse;
}

@keyframes modal-in {
  0% {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }

  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 自定义滚动条 */
.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: rgba(139, 107, 77, 0.2);
  border-radius: 10px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: var(--primary-accent);
}

/* 响应式适配 */
@media (max-width: 640px) {
  .modal-body {
    padding: 20px;
  }

  .book-grid-modal {
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }

  .book-frame {
    height: 240px;
  }

  .modal-header {
    padding: 20px;
  }
}
</style>