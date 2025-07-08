<template>
  <div id="admin-dashboard">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>Book Admin Portal</h2>
      </div>
      <nav class="sidebar-nav">
        <ul>
          <li>
            <router-link to="/dashboard" active-class="active">Dashboard Overview</router-link>
          </li>
          <li>
            <router-link to="/books" active-class="active">Manage Books</router-link>
          </li>
          <li>
            <router-link to="/add-book" active-class="active">Add New Book</router-link>
          </li>
          <li>
            <router-link to="/reviews" active-class="active">Manage Reviews</router-link>
          </li>
          <li>
            <router-link to="/users" active-class="active">Manage Users</router-link>
          </li>
        </ul>
      </nav>
    </aside>

    <main class="main-content">
      <header class="main-header">
        <h1>Welcome, Administrator!</h1>
      </header>
      <div class="content-area">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
// No script setup specific to this template for now,
// as routing will handle component rendering.
</script>

<style scoped>
#admin-dashboard {
  display: flex;
  min-height: 100vh;
  font-family: 'Arial', sans-serif;
  background-color: #f4f7f6;
  color: #333;
}

/* Sidebar Styles */
.sidebar {
  width: 250px;
  background-color: #2c3e50;
  /* Dark blue/grey */
  color: white;
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  text-align: center;
  margin-bottom: 30px;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 1.5em;
  color: #ecf0f1;
  /* Light grey */
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav li {
  margin-bottom: 10px;
}

.sidebar-nav a {
  display: block;
  padding: 10px 15px;
  text-decoration: none;
  color: #bdc3c7;
  /* Muted light grey */
  border-radius: 5px;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.sidebar-nav a:hover,
.sidebar-nav a.active {
  background-color: #34495e;
  /* Slightly lighter dark blue/grey */
  color: #ffffff;
}

/* Main Content Styles */
.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.main-header {
  background-color: #ffffff;
  padding: 20px 30px;
  border-bottom: 1px solid #eee;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.main-header h1 {
  margin: 0;
  font-size: 1.8em;
  color: #2c3e50;
}

.content-area {
  flex-grow: 1;
  padding: 30px;
  background-color: #f4f7f6;
}

/* Basic Router Link Active Class for demonstration */
.router-link-exact-active {
  background-color: #34495e;
  color: #ffffff;
}
</style>