<template>
  <div class="page-container">
    <div class="form-header">
      <div class="title-wrap">
        <span class="back-link">← 返回列表</span>
        <h2>新增图书资源</h2>
        <p>手动录入单本图书，或通过标准 CSV 模板进行批量导入</p>
      </div>
    </div>

    <div class="content-grid">
      <div class="main-form-card card-shadow">
        <form @submit.prevent="submitBook" class="modern-form">
          <div class="form-section">
            <h4 class="section-title">核心信息</h4>
            <div class="form-row">
              <div class="form-group flex-2">
                <label>书名 <span class="required">*</span></label>
                <input type="text" v-model="book.title" placeholder="例如：百年孤独" required>
              </div>
              <div class="form-group flex-1">
                <label>作者 <span class="required">*</span></label>
                <input type="text" v-model="book.author" placeholder="作者姓名" required>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>ISBN 编号</label>
                <input type="text" v-model="book.isbn" placeholder="978-7-xxx-xxx-x">
              </div>
              <div class="form-group">
                <label>出版社</label>
                <input type="text" v-model="book.publisher" placeholder="出版单位全称">
              </div>
            </div>
          </div>

          <div class="form-section">
            <h4 class="section-title">内容与封面</h4>
            <div class="form-group">
              <label>封面图片 URL</label>
              <div class="input-with-preview">
                <input type="url" v-model="book.coverImg" placeholder="https://...">
                <div class="mini-preview" v-if="book.coverImg">
                  <img :src="book.coverImg" alt="Preview">
                </div>
              </div>
            </div>
            <div class="form-group">
              <label>图书简介</label>
              <textarea v-model="book.description" rows="4" placeholder="请输入图书内容的简要介绍..."></textarea>
            </div>
          </div>

          <div class="form-section">
            <h4 class="section-title">规格属性</h4>
            <div class="form-row">
              <div class="form-group">
                <label>出版日期</label>
                <input type="date" v-model="book.publishDate">
              </div>
              <div class="form-group">
                <label>页数</label>
                <input type="number" v-model.number="book.pages" min="1">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>销售价格 (USD)</label>
                <div class="price-input">
                  <span class="currency">$</span>
                  <input type="number" v-model.number="book.price" step="0.01">
                </div>
              </div>
              <div class="form-group">
                <label>图书标签 (英文逗号分隔)</label>
                <input type="text" v-model="genresInput" placeholder="文学, 经典, 虚构">
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="clearForm">重置表单</button>
            <button type="submit" class="btn-primary">
              <span class="icon">✨</span> 确认添加图书
            </button>
          </div>
        </form>
      </div>

      <div class="side-panel">
        <div class="import-card card-shadow">
          <div class="card-header">
            <span class="icon">📂</span>
            <h4>快速批量导入</h4>
          </div>
          <div class="drop-zone" @click="$refs.csvFileInput.click()">
            <input type="file" ref="csvFileInput" @change="handleCSVUpload" accept=".csv" hidden>
            <div class="dz-content">
              <span class="dz-icon">📤</span>
              <p class="dz-text">点击上传 CSV 文件</p>
              <p class="dz-hint">自动解析首行数据</p>
            </div>
          </div>
          <div class="import-tips">
            <h5>字段要求：</h5>
            <ul>
              <li>必须包含: title, author</li>
              <li>可选: isbn, price, genres (分号分隔)</li>
            </ul>
          </div>
        </div>

        <div class="help-card card-shadow">
          <h4>填写帮助</h4>
          <p>1. 带有星号的字段为必填项。</p>
          <p>2. 封面图建议比例为 3:4，宽度不小于 600px。</p>
          <p>3. 价格请填写数值，系统会自动格式化。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'

const csvFileInput = ref(null)

const book = ref({
  title: '',
  author: '',
  isbn: '',
  coverImg: '',
  description: '',
  publisher: '',
  publishDate: '',
  pages: null,
  price: null,
  genres: [],
})

const genresInput = ref('')

watch(genresInput, (newValue) => {
  book.value.genres = newValue.split(',').map(genre => genre.trim()).filter(genre => genre.length > 0)
})

const handleCSVUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const csv = e.target.result
      const lines = csv.split('\n')
      const headers = lines[0].split(',').map(h => h.trim().toLowerCase())

      if (lines.length > 1) {
        const firstDataLine = lines[1].split(',')
        const csvData = {}

        headers.forEach((header, index) => {
          if (firstDataLine[index]) {
            csvData[header] = firstDataLine[index].trim().replace(/"/g, '')
          }
        })

        // Map CSV data to form fields
        if (csvData.title) book.value.title = csvData.title
        if (csvData.author) book.value.author = csvData.author
        if (csvData.isbn) book.value.isbn = csvData.isbn
        if (csvData.description) book.value.description = csvData.description
        if (csvData.publisher) book.value.publisher = csvData.publisher
        if (csvData.publishdate || csvData['publish date']) {
          book.value.publishDate = csvData.publishdate || csvData['publish date']
        }
        if (csvData.pages) book.value.pages = parseInt(csvData.pages)
        if (csvData.price) book.value.price = parseFloat(csvData.price)
        if (csvData.genres) {
          genresInput.value = csvData.genres
          book.value.genres = csvData.genres.split(';').map(g => g.trim())
        }

        alert('CSV data imported successfully! Please review and submit.')
      }
    } catch (error) {
      alert('Error parsing CSV file. Please check the format.')
      console.error('CSV parsing error:', error)
    }
  }
  reader.readAsText(file)
}

const submitBook = async () => {
  try {
    const response = await axios.post('/service-b/api/books', book.value)
    alert('Book added successfully!')
    clearForm()
  } catch (error) {
    console.error('Error adding book:', error)
    alert('Failed to add book. Please try again.')
  }
}

const clearForm = () => {
  book.value = {
    title: '',
    author: '',
    isbn: '',
    coverImg: '',
    description: '',
    publisher: '',
    publishDate: '',
    pages: null,
    price: null,
    genres: [],
  }
  genresInput.value = ''
  if (csvFileInput.value) {
    csvFileInput.value.value = ''
  }
}
</script>

<style scoped>
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f8fafc;
  min-height: 100vh;
}

/* 顶部样式 */
.form-header {
  margin-bottom: 30px;
}

.back-link {
  color: #64748b;
  font-size: 0.9rem;
  cursor: pointer;
  display: block;
  margin-bottom: 10px;
}

.form-header h2 {
  color: #1e293b;
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
}

.form-header p {
  color: #64748b;
  margin-top: 5px;
}

/* 布局 */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 30px;
}

.main-form-card {
  background: #fff;
  border-radius: 16px;
  padding: 35px;
}

/* 表单细节 */
.section-title {
  font-size: 1rem;
  color: #3b82f6;
  border-left: 4px solid #3b82f6;
  padding-left: 12px;
  margin: 30px 0 20px 0;
}

.section-title:first-child {
  margin-top: 0;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.flex-2 {
  flex: 2;
}

.flex-1 {
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.form-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

.required {
  color: #ef4444;
}

input,
textarea {
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.2s;
  background: #fdfdfd;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  background: #fff;
}

/* 封面预览辅助 */
.input-with-preview {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.input-with-preview input {
  flex: 1;
}

.mini-preview {
  width: 50px;
  height: 65px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid #e2e8f0;
}

.mini-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 价格前缀 */
.price-input {
  position: relative;
  display: flex;
  align-items: center;
}

.currency {
  position: absolute;
  left: 14px;
  color: #94a3b8;
  font-weight: 600;
}

.price-input input {
  padding-left: 30px;
  width: 100%;
}

/* 按钮操作 */
.form-actions {
  margin-top: 40px;
  padding-top: 25px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.btn-primary {
  background: #1e293b;
  color: white;
  padding: 12px 28px;
  border-radius: 10px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #0f172a;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
  padding: 12px 24px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
}

/* 右侧边栏 */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.import-card,
.help-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.card-header h4 {
  margin: 0;
  color: #1e293b;
}

.drop-zone {
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  padding: 30px 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.drop-zone:hover {
  border-color: #3b82f6;
  background: #f0f7ff;
}

.dz-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 10px;
}

.dz-text {
  font-weight: 600;
  color: #475569;
  margin: 0;
}

.dz-hint {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 5px;
}

.import-tips {
  margin-top: 15px;
  background: #f8fafc;
  padding: 12px;
  border-radius: 8px;
}

.import-tips h5 {
  font-size: 0.8rem;
  margin: 0 0 8px 0;
  color: #64748b;
}

.import-tips ul {
  padding-left: 18px;
  margin: 0;
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.6;
}

.help-card h4 {
  font-size: 0.9rem;
  margin-bottom: 12px;
}

.help-card p {
  font-size: 0.8rem;
  color: #64748b;
  line-height: 1.5;
  margin-bottom: 8px;
}

.card-shadow {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
}

@media (max-width: 992px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .side-panel {
    order: -1;
  }
}
</style>