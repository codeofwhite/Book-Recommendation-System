<template>
  <div class="admin-panel-card">
    <h2>Dashboard Overview</h2>
    <p>Welcome to your Book Management Dashboard. Here you can see a quick summary of your data.</p>
    <div class="stats-grid">
      <div class="stat-item">
        <h3>Total Books</h3>
        <p class="stat-number">1250</p>
      </div>
      <div class="stat-item">
        <h3>Pending Reviews</h3>
        <p class="stat-number">15</p>
      </div>
      <div class="stat-item">
        <h3>New Users This Week</h3>
        <p class="stat-number">23</p>
      </div>
      <div class="stat-item">
        <h3>Avg. Book Rating</h3>
        <p class="stat-number">4.2 <span class="stars">★★★★☆</span></p>
      </div>
    </div>
  </div>
</template>

<script setup>
// You would fetch actual data here
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.stat-item {
  background-color: #ecf0f1;
  padding: 15px;
  border-radius: 5px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
}

.stat-item h3 {
  margin-top: 0;
  color: #34495e;
  font-size: 1.1em;
}

.stat-item .stat-number {
  font-size: 2.2em;
  font-weight: bold;
  color: #3498db; /* Blue */
  margin: 10px 0 0;
}

.stat-item .stars {
  color: #f1c40f; /* Yellow */
}
</style>