<template>
  <div class="epub-reader-container">
    <div v-if="isLoading" class="status-message">
      <p>📖 Loading...</p>
    </div>
    <div v-if="error" class="status-message error">
      <p>❌ Erro: This book cannot be loaded.</p>
      <p><small>{{ error }}</small></p>
      <button @click="goBack">‹‹</button>
    </div>
    
    <div v-if="!isLoading && !error" class="reader-header">
      <button @click="goBack" class="back-button">‹‹</button>
    </div>
    
    <div id="epub-viewer-area" v-show="!isLoading && !error" :class="{ 'eye-protect-mode': isEyeProtectMode }"></div>

    <div v-if="!isLoading && !error" class="epub-reader-controls">
      <button @click="prevPage" class="pagination-button">‹ Prev</button>

      <div class="center-controls">
        <div class="page-jump-controls">
          <input
            type="number"
            v-model.number="targetLocation"
            @keyup.enter="jumpToLocation"
            class="page-input"
            :min="1"
            :max="totalPages"
          />
          <button @click="jumpToLocation" class="jump-button">Jump to</button>
          <span v-if="totalPages > 0" class="page-display">/ {{ totalPages }} page</span>
        </div>

        <div class="appearance-controls">
          <div class="font-size-controls">
            <button @click="setFontSize('100%')" :class="{ active: currentFontSize === '100%' }">S</button>
            <button @click="setFontSize('115%')" :class="{ active: currentFontSize === '115%' }">M</button>
            <button @click="setFontSize('130%')" :class="{ active: currentFontSize === '130%' }">L</button>
          </div>
          <button @click="toggleEyeProtectMode" class="eye-protect-button" :class="{ active: isEyeProtectMode }">
            {{ isEyeProtectMode ? 'Change Background' : 'Change Background' }}
          </button>
        </div>
      </div>

      <button @click="nextPage" class="pagination-button">Next ›</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import ePub from 'epubjs';

const route = useRoute();
const router = useRouter();

const book = ref(null);
const rendition = ref(null);
const isLoading = ref(true);
const error = ref(null);

const totalPages = ref(0);
const targetLocation = ref(1);
const currentFontSize = ref('100%');
const isEyeProtectMode = ref(false); // 护眼模式状态

// 切换护眼模式
const toggleEyeProtectMode = () => {
  isEyeProtectMode.value = !isEyeProtectMode.value;
};

// --- Control Functions ---
const nextPage = () => rendition.value?.next();
const prevPage = () => rendition.value?.prev();

const jumpToLocation = () => {
  if (!book.value || !targetLocation.value) return;
  const cfi = book.value.locations.cfiFromLocation(targetLocation.value - 1);
  rendition.value.display(cfi);
};

const setFontSize = (size) => {
  currentFontSize.value = size;
  rendition.value?.themes.fontSize(size);
};

const onRelocated = (location) => {
  targetLocation.value = location.start.location + 1;
};

// --- Keyboard Navigation Handler ---
const handleKeyPress = (event) => {
  if (event.target.tagName.toUpperCase() === 'INPUT') {
    return;
  }
  if (event.key === 'ArrowRight') {
    nextPage();
  }
  if (event.key === 'ArrowLeft') {
    prevPage();
  }
};

/**
 * 加载 EPUB 文件
 */
const loadEpub = async (bookId) => {
  isLoading.value = true;
  error.value = null;

  try {
    const epubFileName = 'Twilight.epub';
    const epubFileUrl = `/TestEpub/${epubFileName}`;
    
    book.value = ePub(epubFileUrl);
    await book.value.ready;

    await book.value.locations.generate(1024);
    totalPages.value = book.value.locations.length();

    rendition.value = book.value.renderTo('epub-viewer-area', {
      width: '100%',
      height: '100%',
      spread: 'auto',
      allowScriptedContent: true,
    });
    
    rendition.value.on('relocated', onRelocated);
    rendition.value.themes.fontSize(currentFontSize.value);
    await rendition.value.display();

    targetLocation.value = 1;
    jumpToLocation();
  } catch (err) {
    console.error('EPUB加载错误:', err);
    error.value = `加载失败: ${err.message}.`;
  } finally {
    isLoading.value = false;
  }
};

const goBack = () => router.back();

onMounted(() => {
  window.addEventListener('keydown', handleKeyPress);
  const bookId = route.params.bookId;
  if (bookId) loadEpub(bookId);
  else {
    error.value = '未提供书籍ID。';
    isLoading.value = false;
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyPress);
  if (book.value) book.value.destroy();
  if (rendition.value) {
    rendition.value.off('relocated', onRelocated);
    rendition.value.destroy();
  }
});
</script>

<style scoped>
.epub-reader-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  position: relative;
}

.reader-header {
  width: 100%;
  padding: 0.5rem;
  display: flex;
  justify-content: flex-start;
}

.back-button {
  position: absolute;
  top: 1rem; left: 0.2rem;
  background-color: transparent;
  color: black;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 5px;
  font-size: 2rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-left: 1rem;
  z-index: 10;
}

.back-button:hover {
  background-color: #8d6e63;
  color:white
}

#epub-viewer-area {
  flex-grow: 1;
  width: 100%;
  max-width: 1200px;
  height: 90vh;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  background-color: #ffffff;
  transition: background-color 0.3s ease;
}

#epub-viewer-area.eye-protect-mode {
  background-color: #fffaf0;
}

.epub-reader-controls {
  flex-shrink: 0;
  width: 100%;
  max-width: 800px;
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.center-controls {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.appearance-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-button {
  background-color: #8a6d5d;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}
.pagination-button:hover {
  background-color: #6b5346;
}

.page-jump-controls, .font-size-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-input {
  width: 50px;
  text-align: center;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.page-input::-webkit-outer-spin-button,
.page-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.page-input[type=number] {
  -moz-appearance: textfield;
}

.page-display {
  font-size: 1rem;
  color: #333;
}

.jump-button {
  background-color: #f8f8f8;
  border: 1px solid #ccc;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.font-size-controls button {
  background-color: #f8f8f8;
  border: 1px solid #ccc;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  line-height: 1;
}

.font-size-controls button.active {
  background-color: #6b5346;
  color: white;
  border-color: #6b5346;
}

.eye-protect-button {
  background-color: #f8f8f8;
  border: 1px solid #ccc;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  line-height: 1;
  transition: all 0.3s ease;
}

.eye-protect-button.active {
  background-color: #8d6e63;
  color: white;
  border-color: #8d6e63;
}

.status-message {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 1.5rem;
  text-align: center;
  padding: 20px;
}
.status-message.error {
  color: #D8000C;
}
</style>