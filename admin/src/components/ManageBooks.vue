<template>
  <div class="admin-panel-card">
    <h2>Manage Books</h2>
    <p>View, edit, or delete existing book entries.</p>

    <div class="search-filter-bar">
      <input type="text" placeholder="Search by title, author, ISBN..." class="search-input">
      <button class="search-button">Search</button>
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Title</th>
          <th>Author</th>
          <th>ISBN</th>
          <th>Rating</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>1</td>
          <td>The Great Adventure</td>
          <td>Jane Doe</td>
          <td>978-1234567890</td>
          <td>4.5</td>
          <td>
            <button class="action-button edit-button">Edit</button>
            <button class="action-button delete-button">Delete</button>
          </td>
        </tr>
        <tr>
          <td>2</td>
          <td>Mysteries of the Ancient World</td>
          <td>John Smith</td>
          <td>978-0987654321</td>
          <td>3.9</td>
          <td>
            <button class="action-button edit-button">Edit</button>
            <button class="action-button delete-button">Delete</button>
          </td>
        </tr>
        </tbody>
    </table>

    <div class="pagination">
      <button>&laquo; Previous</button>
      <span>Page 1 of 10</span>
      <button>Next &raquo;</button>
    </div>
  </div>
</template>

<script setup>
// Data fetching, editing logic, deletion logic will go here.
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

.search-filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex-grow: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1em;
}

.search-button {
  padding: 10px 20px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background-color: #2980b9;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.data-table th,
.data-table td {
  border: 1px solid #eee;
  padding: 12px 15px;
  text-align: left;
}

.data-table th {
  background-color: #f2f2f2;
  font-weight: bold;
  color: #555;
}

.data-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

.data-table tbody tr:hover {
  background-color: #f0f0f0;
}

.action-button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
  transition: background-color 0.3s ease;
}

.edit-button {
  background-color: #f39c12; /* Orange */
  color: white;
}

.edit-button:hover {
  background-color: #e67e22;
}

.delete-button {
  background-color: #e74c3c; /* Red */
  color: white;
}

.delete-button:hover {
  background-color: #c0392b;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 10px;
}

.pagination button {
  padding: 10px 15px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.pagination button:hover:not(:disabled) {
  background-color: #2980b9;
}

.pagination button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.pagination span {
  font-weight: bold;
  color: #555;
}
</style>