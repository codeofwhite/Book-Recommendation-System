<template>
  <div class="epub-reader-container">
    <div v-if="isLoading" class="status-message">
      <p>📖 正在为您翻开书卷...</p>
    </div>
    <div v-if="error" class="status-message error">
      <p>❌ 无法加载此书。文件可能已损坏或不存在。</p>
      <button @click="goBack">返回详情页</button>
    </div>
    <div id="epub-viewer-area"></div>
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

/**
 * 加载 EPUB 文件
 * @param {string} bookId - 书籍的ID
 */
const loadEpub = async (bookId) => {
  isLoading.value = true;
  error.value = null;

  try {
    let epubFileUrl;

    // ======================== 前端测试代码块 (开始) ========================
    // 在前端测试模式下，我们忽略真实的后端 API 调用，
    // 直接构造指向 public 文件夹下测试文件的路径。
    // 这里的逻辑可以根据不同的测试 bookId 返回不同的本地文件。
    if (bookId === '2.Harry_Potter_and_the_Order_of_the_Phoenix') {
        epubFileUrl = '/epubs/moby-dick.epub'; // 对应准备工作中添加的文件
    } else {
        // 可以为其他测试 ID 设置备用文件
        // epubFileUrl = '/epubs/another-book.epub'; 
        
        // 如果没有匹配的测试 ID，可以抛出错误或加载默认文件
        console.warn(`未找到ID为 ${bookId} 的本地测试文件，请检查 EpubReader.vue 中的测试逻辑。`);
        epubFileUrl = '/epubs/moby-dick.epub'; // 加载一个默认的作为后备
    }
    console.warn(`--- 前端测试模式 ---: 正在从本地路径 "${epubFileUrl}" 加载 EPUB。`);
    // ======================== 前端测试代码块 (结束) ========================
    
    /*
    // --- 生产环境代码 ---
    // 在实际部署时，你应该移除上面的测试代码块，并使用下面的代码
    // const epubFileUrl = `/service-b/api/books/${bookId}/epub`;
    */
    
    // 修复：使用 fetch API 获取文件内容
    const response = await fetch(epubFileUrl);
    if (!response.ok) {
      throw new Error(`无法加载EPUB文件: ${response.status} ${response.statusText}`);
    }
    
    // 获取ArrayBuffer格式的文件内容
    const arrayBuffer = await response.arrayBuffer();
    
    // 使用ArrayBuffer创建ePub实例
    book.value = ePub(arrayBuffer);
    
    // 等待书籍加载完成
    await book.value.ready;

    // 将书籍渲染到指定的 div 中
    rendition.value = book.value.renderTo('epub-viewer-area', {
      width: '100%',
      height: '100vh',
      spread: 'none' // 禁用双页视图
    });
    
    // 显示第一页
    await rendition.value.display();
    
  } catch (err) {
    console.error('EPUB 加载失败:', err);
    error.value = err.message || '无法加载EPUB文件';
  } finally {
    isLoading.value = false;
  }
};

const goBack = () => {
  router.back();
};

onMounted(() => {
  const bookId = route.params.bookId;
  if (bookId) {
    loadEpub(bookId);
  } else {
    error.value = '未提供书籍ID。';
    isLoading.value = false;
  }
});

onBeforeUnmount(() => {
  // 组件销毁时，销毁 ePub 实例以释放内存
  if (book.value) {
    book.value.destroy();
  }
  if (rendition.value) {
    rendition.value.destroy();
  }
});
</script>

<style scoped>
.epub-reader-container {
  width: 100%;
  height: 100vh;
  position: relative;
}

#epub-viewer-area {
  width: 100%;
  height: 100vh;
}

.status-message {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 1.5rem;
}

.status-message.error {
  color: #D8000C; /* 红色 */
}
</style>