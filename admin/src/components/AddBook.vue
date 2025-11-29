<template>
  <div class="admin-panel-card">
    <div class="header-section">
      <h2>Add New Book</h2>
      <p>Fill out the form below to add a new book to the collection, or import from CSV file.</p>
    </div>

    <!-- CSV Import Section -->
    <div class="csv-import-section">
      <h3>📁 Import from CSV</h3>
      <div class="csv-import-area">
        <input type="file" ref="csvFileInput" @change="handleCSVUpload" accept=".csv" class="csv-input" id="csv-upload">
        <label for="csv-upload" class="csv-upload-label">
          <span class="upload-icon">📤</span>
          Choose CSV File
        </label>
        <p class="csv-help-text">
          CSV should contain columns: title, author, isbn, description, publisher, publishDate, pages, price, genres
        </p>
      </div>
    </div>

    <div class="divider">
      <span>OR</span>
    </div>

    <!-- Manual Form -->
    <form @submit.prevent="submitBook" class="book-form">
      <div class="form-row">
        <div class="form-group">
          <label for="title">📖 Title *</label>
          <input type="text" id="title" v-model="book.title" required>
        </div>
        <div class="form-group">
          <label for="author">✍️ Author *</label>
          <input type="text" id="author" v-model="book.author" required>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="isbn">🔢 ISBN</label>
          <input type="text" id="isbn" v-model="book.isbn" placeholder="978-0-123456-78-9">
        </div>
        <div class="form-group">
          <label for="publisher">🏢 Publisher</label>
          <input type="text" id="publisher" v-model="book.publisher">
        </div>
      </div>

      <div class="form-group">
        <label for="coverImg">🖼️ Cover Image URL</label>
        <input type="url" id="coverImg" v-model="book.coverImg" placeholder="https://example.com/cover.jpg">
      </div>

      <div class="form-group">
        <label for="description">📝 Description</label>
        <textarea id="description" v-model="book.description" rows="4"
          placeholder="Enter book description..."></textarea>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="publishDate">📅 Publish Date</label>
          <input type="date" id="publishDate" v-model="book.publishDate">
        </div>
        <div class="form-group">
          <label for="pages">📄 Pages</label>
          <input type="number" id="pages" v-model.number="book.pages" min="1">
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="price">💰 Price ($)</label>
          <input type="number" id="price" v-model.number="book.price" step="0.01" min="0">
        </div>
        <div class="form-group">
          <label for="genres">🏷️ Genres</label>
          <input type="text" id="genres" v-model="genresInput" placeholder="Fiction, Fantasy, Sci-Fi">
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="clear-button" @click="clearForm">Clear Form</button>
        <button type="submit" class="submit-button">
          <span class="button-icon">➕</span>
          Add Book
        </button>
      </div>
    </form>
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
.admin-panel-card {
  background-color: #ffffff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.header-section h2 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1.8em;
  font-weight: 600;
}

.header-section p {
  color: #7f8c8d;
  margin-bottom: 30px;
  font-size: 1.1em;
}

.csv-import-section {
  background-color: #f8f9fa;
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 30px;
  border: 2px dashed #dee2e6;
}

.csv-import-section h3 {
  margin: 0 0 16px 0;
  color: #495057;
  font-size: 1.2em;
}

.csv-import-area {
  text-align: center;
}

.csv-input {
  display: none;
}

.csv-upload-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background-color: #007bff;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.csv-upload-label:hover {
  background-color: #0056b3;
}

.upload-icon {
  font-size: 1.2em;
}

.csv-help-text {
  margin-top: 12px;
  color: #6c757d;
  font-size: 0.9em;
}

.divider {
  text-align: center;
  margin: 30px 0;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #dee2e6;
}

.divider span {
  background-color: white;
  padding: 0 16px;
  color: #6c757d;
  font-weight: 500;
}

.book-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #495057;
  font-size: 1em;
}

.form-group input,
.form-group textarea {
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1em;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.clear-button {
  padding: 12px 24px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.clear-button:hover {
  background-color: #5a6268;
}

.submit-button {
  padding: 12px 24px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.submit-button:hover {
  background-color: #218838;
}

.button-icon {
  font-size: 1.1em;
}
</style>