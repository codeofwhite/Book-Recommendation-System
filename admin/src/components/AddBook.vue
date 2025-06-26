<template>
  <div class="admin-panel-card">
    <h2>Add New Book</h2>
    <p>Fill out the form below to add a new book to the collection.</p>

    <form @submit.prevent="submitBook" class="book-form">
      <div class="form-group">
        <label for="title">Title:</label>
        <input type="text" id="title" v-model="book.title" required>
      </div>

      <div class="form-group">
        <label for="author">Author:</label>
        <input type="text" id="author" v-model="book.author" required>
      </div>

      <div class="form-group">
        <label for="isbn">ISBN:</label>
        <input type="text" id="isbn" v-model="book.isbn">
      </div>

      <div class="form-group">
        <label for="coverImg">Cover Image URL:</label>
        <input type="url" id="coverImg" v-model="book.coverImg">
      </div>

      <div class="form-group">
        <label for="description">Description:</label>
        <textarea id="description" v-model="book.description" rows="6"></textarea>
      </div>

      <div class="form-group">
        <label for="publisher">Publisher:</label>
        <input type="text" id="publisher" v-model="book.publisher">
      </div>

      <div class="form-group">
        <label for="publishDate">Publish Date:</label>
        <input type="date" id="publishDate" v-model="book.publishDate">
      </div>

      <div class="form-group">
        <label for="pages">Pages:</label>
        <input type="number" id="pages" v-model.number="book.pages">
      </div>

      <div class="form-group">
        <label for="price">Price ($):</label>
        <input type="number" id="price" v-model.number="book.price" step="0.01">
      </div>

      <div class="form-group">
        <label for="genres">Genres (comma-separated):</label>
        <input type="text" id="genres" v-model="genresInput" placeholder="Fiction, Fantasy, Sci-Fi">
      </div>

      <button type="submit" class="submit-button">Add Book</button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

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
  genres: [], // Array for genres
  // Add other book properties here based on your data model
});

const genresInput = ref(''); // For comma-separated genre input

// Watch for changes in genresInput and update book.genres array
watch(genresInput, (newValue) => {
  book.value.genres = newValue.split(',').map(genre => genre.trim()).filter(genre => genre.length > 0);
});

const submitBook = () => {
  console.log('Submitting book:', book.value);
  // Here you would typically send this data to your backend API
  // e.g., axios.post('http://localhost:5000/api/books', book.value)
  // After successful submission, you might clear the form or navigate
  alert('Book added (not truly saved yet, check console)!');
  // Reset form
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
  };
  genresInput.value = '';
};
</script>

<style scoped>
.admin-panel-card {
  background-color: #ffffff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.6em;
  border-bottom: 2px solid #ecf0f1;
  padding-bottom: 10px;
}

.book-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
  font-size: 0.95em;
}

.form-group input[type="text"],
.form-group input[type="url"],
.form-group input[type="date"],
.form-group input[type="number"],
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1em;
  width: 100%;
  box-sizing: border-box; /* Include padding in width */
}

.form-group textarea {
  resize: vertical; /* Allow vertical resizing */
}

.submit-button {
  align-self: flex-start; /* Align button to the left */
  padding: 12px 25px;
  background-color: #27ae60; /* Green */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1.1em;
  transition: background-color 0.3s ease;
  margin-top: 10px;
}

.submit-button:hover {
  background-color: #229a58;
}
</style>