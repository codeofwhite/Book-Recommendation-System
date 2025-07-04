
<template>
  <div class="epub-reader-container">
    <div v-if="isLoading" class="status-message">
      <p>📖 正在为您翻开书卷...</p>
      <p v-if="isGeneratingLocations" style="font-size: 1rem; margin-top: 10px;">(首次加载正在生成页码, 请稍候...)</p>
    </div>
    <div v-if="error" class="status-message error">
      <p>❌ 无法加载此书。</p>
      <p><small>{{ error }}</small></p>
      <button @click="goBack">返回详情页</button>
    </div>
    
    <div id="epub-viewer-area"></div>

    <div v-if="!isLoading && !error" class="epub-reader-controls">
      <button @click="prevPage" class="pagination-button">‹ 上一页</button>

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
          <button @click="jumpToLocation" class="jump-button">跳转</button>
          <span v-if="totalPages > 0" class="page-display">/ {{ totalPages }} 页</span>
        </div>

        <div class="font-size-controls">
          <button @click="setFontSize('85%')" :class="{ active: currentFontSize === '85%' }">小</button>
          <button @click="setFontSize('100%')" :class="{ active: currentFontSize === '100%' }">中</button>
          <button @click="setFontSize('125%')" :class="{ active: currentFontSize === '125%' }">大</button>
        </div>
      </div>

      <button @click="nextPage" class="pagination-button">下一页 ›</button>
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
const isGeneratingLocations = ref(false);
const error = ref(null);

const totalPages = ref(0);
const targetLocation = ref(1);
const currentFontSize = ref('100%'); // Default font size

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
  // Do not turn pages if the user is focused on an input field
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

    isGeneratingLocations.value = true;
    await book.value.locations.generate(1024);
    totalPages.value = book.value.locations.length();
    isGeneratingLocations.value = false;

    rendition.value = book.value.renderTo('epub-viewer-area', {
      
      width: '100%',
      height: '100%',
      spread: 'auto',
      allowScriptedContent: true,
    });
    
    rendition.value.on('relocated', onRelocated);
    
    // Apply the default font size once the rendition is ready
    rendition.value.themes.fontSize(currentFontSize.value);

    await rendition.value.display();

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
}

#epub-viewer-area {
  flex-grow: 1;
  width: 100%;
  max-width: 1200px;
  height: 90vh;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  background-color: #ffffff;
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
