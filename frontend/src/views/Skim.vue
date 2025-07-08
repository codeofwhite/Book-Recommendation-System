<template>
  <div class="manuscript-review-chamber">
    <!-- Main Content Area -->
    <div class="parchment-scroll-container">
      <!-- Left Panel: Book Details -->
      <div class="tome-details-panel">
        <div class="book-showcase-card">
          <div class="book-hero-section">
            <div class="illuminated-cover-section">
              <img :src="currentBook.coverImage" :alt="currentBook.title" class="featured-tome-cover" />
              <div class="cover-ornament"></div>
              <div class="cover-glow"></div>
            </div>
            
            <div class="book-primary-info">
              <h1 class="tome-grand-title">{{ currentBook.title }}</h1>
              <h2 class="tome-author-inscription">{{ currentBook.author }}</h2>
              
              <div class="celestial-rating-display">
                <span class="golden-stars">{{ '★'.repeat(Math.round(currentBook.rating)) }}{{ '☆'.repeat(5 - Math.round(currentBook.rating)) }}</span>
                <span class="rating-whispers">({{ currentBook.rating }} from {{ currentBook.totalRatings }} souls)</span>
              </div>
              
              <div class="quick-details-ribbon">
                <span class="detail-badge">{{ currentBook.genre }}</span>
                <span class="detail-badge">{{ currentBook.publishYear }}</span>
                <span class="detail-badge">${{ currentBook.price }}</span>
              </div>
            </div>
          </div>

          <div class="book-detailed-section" :key="currentBook.id">
            <div class="tome-essence-details">
              <div class="detail-scroll">
                <span class="detail-label">Genre:</span>
                <span class="detail-value">{{ currentBook.genre }}</span>
              </div>
              <div class="detail-scroll">
                <span class="detail-label">Published:</span>
                <span class="detail-value">{{ currentBook.publishYear }}</span>
              </div>
              <div class="detail-scroll">
                <span class="detail-label">Pages:</span>
                <span class="detail-value">{{ currentBook.pages }}</span>
              </div>
              <div class="detail-scroll">
                <span class="detail-label">Price:</span>
                <span class="detail-value">${{ currentBook.price }}</span>
              </div>
            </div>
            
            <div class="tome-synopsis">
              <h3 class="synopsis-title">Synopsis</h3>
              <p class="synopsis-text">{{ currentBook.description }}</p>
            </div>
            
            <div class="genre-seals-collection">
              <span v-for="tag in currentBook.tags" :key="tag" class="genre-seal-tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Book Review -->
      <div class="review-manuscript-panel">
        <div class="review-parchment-card">
          <div class="review-header-scroll">
            <h2 class="review-chamber-title">Scholarly Discourse</h2>
            <div class="review-navigation-quills">
              <button 
                @click="previousReview" 
                :disabled="currentReviewIndex === 0"
                class="nav-quill-button prev-quill"
                :class="{ 'quill-disabled': currentReviewIndex === 0 }"
              >
                <div class="quill-feather">
                  <span class="quill-shaft"></span>
                  <span class="quill-tip">‹</span>
                </div>
                <span class="quill-label">Previous</span>
              </button>
              
              <div class="review-counter-ornate">
                <span class="counter-decoration">❦</span>
                <span class="review-counter">{{ currentReviewIndex + 1 }} of {{ reviews.length }}</span>
                <span class="counter-decoration">❦</span>
              </div>
              
              <button 
                @click="nextReview" 
                :disabled="currentReviewIndex === reviews.length - 1"
                class="nav-quill-button next-quill"
                :class="{ 'quill-disabled': currentReviewIndex === reviews.length - 1 }"
              >
                <span class="quill-label">Next</span>
                <div class="quill-feather">
                  <span class="quill-shaft"></span>
                  <span class="quill-tip">›</span>
                </div>
              </button>
            </div>
          </div>

          <div class="review-content-scroll" :key="currentReview.id">
            <div class="reviewer-seal">
              <div class="reviewer-avatar">
                <img :src="currentReview.reviewerAvatar" :alt="currentReview.reviewerName" />
              </div>
              <div class="reviewer-inscription">
                <h4 class="reviewer-name">{{ currentReview.reviewerName }}</h4>
                <p class="reviewer-title">{{ currentReview.reviewerTitle }}</p>
                <div class="review-celestial-rating">
                  <span class="review-stars">{{ '★'.repeat(currentReview.rating) }}{{ '☆'.repeat(5 - currentReview.rating) }}</span>
                </div>
              </div>
            </div>

            <div class="review-manuscript-text">
              <div class="opening-quote-mark">"</div>
              <p class="review-text">{{ currentReview.reviewText }}</p>
              <div class="closing-quote-mark">"</div>
            </div>

            <div class="review-metadata-scroll">
              <span class="review-date">Inscribed on {{ formatDate(currentReview.date) }}</span>
              <span class="review-helpful">{{ currentReview.helpfulCount }} found this enlightening</span>
            </div>
          </div>

          <!-- Bookmark Button -->
          <div class="bookmark-chamber">
            <button 
              @click="toggleBookmark"
              class="bookmark-quill-button"
              :class="{ 'is-bookmarked': isCurrentReviewBookmarked }"
              @mouseenter="onBookmarkHover"
              @mouseleave="onBookmarkLeave"
            >
              <div class="bookmark-icon-container">
                <span class="bookmark-icon">🔖</span>
                <span class="bookmark-sparkles" v-if="showSparkles">✨</span>
              </div>
              <span class="bookmark-text">
                {{ isCurrentReviewBookmarked ? 'Preserved in thy Collection' : 'Preserve this Wisdom' }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Reactive data
const currentReviewIndex = ref(0)
const bookmarkedReviews = ref(new Set())
const showSparkles = ref(false)

// Mock data for reviews and books
const reviews = ref([
  {
    id: 1,
    bookId: 'book1',
    reviewerName: 'Eleanor Whitmore',
    reviewerTitle: 'Professor of Classical Literature',
    reviewerAvatar: '/placeholder.svg?height=60&width=60',
    rating: 5,
    reviewText: 'This masterpiece transcends the boundaries of conventional storytelling, weaving together threads of philosophy, adventure, and profound human insight. The author\'s prose flows like liquid gold, each sentence carefully crafted to resonate with the reader\'s soul. I found myself completely immersed in this world, unable to put the book down until the very last page. The character development is extraordinary, and the themes explored are both timeless and remarkably relevant to our modern age.',
    date: '2024-12-15',
    helpfulCount: 127
  },
  {
    id: 2,
    bookId: 'book2',
    reviewerName: 'Marcus Thornfield',
    reviewerTitle: 'Literary Critic & Author',
    reviewerAvatar: '/placeholder.svg?height=60&width=60',
    rating: 4,
    reviewText: 'A compelling narrative that challenges readers to question their assumptions about society and human nature. While the pacing occasionally falters in the middle chapters, the author\'s brilliant use of symbolism and metaphor more than compensates for any structural weaknesses. The dialogue is sharp and authentic, bringing each character to vivid life. This is the kind of book that stays with you long after reading, prompting deep reflection and discussion.',
    date: '2024-12-10',
    helpfulCount: 89
  },
  {
    id: 3,
    bookId: 'book3',
    reviewerName: 'Dr. Sophia Chen',
    reviewerTitle: 'Philosophy Department Head',
    reviewerAvatar: '/placeholder.svg?height=60&width=60',
    rating: 5,
    reviewText: 'An intellectual tour de force that seamlessly blends entertainment with profound philosophical inquiry. The author demonstrates remarkable erudition while maintaining accessibility for general readers. Each chapter builds upon the last, creating a crescendo of understanding that culminates in a deeply satisfying conclusion. The exploration of moral ambiguity and the nature of truth is handled with exceptional nuance and sophistication.',
    date: '2024-12-08',
    helpfulCount: 156
  }
])

const books = ref([
  {
    id: 'book1',
    title: 'The Luminous Codex of Eternal Wisdom',
    author: 'Arabella Nightingale',
    coverImage: '/placeholder.svg?height=400&width=280',
    rating: 4.8,
    totalRatings: 2847,
    genre: 'Philosophical Fiction',
    publishYear: 2023,
    pages: 487,
    price: 24.99,
    description: 'A profound exploration of human consciousness and the nature of reality, told through the journey of a young scholar who discovers an ancient manuscript that challenges everything she believes about existence. This luminous work weaves together elements of mysticism, science, and philosophy in a narrative that is both intellectually stimulating and emotionally resonant.',
    tags: ['Philosophy', 'Mystery', 'Literary Fiction', 'Metaphysical']
  },
  {
    id: 'book2',
    title: 'Shadows of the Forgotten Realm',
    author: 'Cornelius Blackwood',
    coverImage: '/placeholder.svg?height=400&width=280',
    rating: 4.3,
    totalRatings: 1923,
    genre: 'Dark Fantasy',
    publishYear: 2022,
    pages: 623,
    price: 27.50,
    description: 'In a world where magic has been forgotten and technology reigns supreme, a young archaeologist uncovers artifacts that suggest a different history than what has been recorded. As she delves deeper into the mystery, she discovers that some knowledge was hidden for good reason, and that the shadows of the past are not as dormant as they appear.',
    tags: ['Fantasy', 'Adventure', 'Archaeological Mystery', 'Dark Magic']
  },
  {
    id: 'book3',
    title: 'The Cartographer of Lost Souls',
    author: 'Isadora Moonwhisper',
    coverImage: '/placeholder.svg?height=400&width=280',
    rating: 4.9,
    totalRatings: 3156,
    genre: 'Magical Realism',
    publishYear: 2024,
    pages: 398,
    price: 22.95,
    description: 'A haunting and beautiful tale of a woman who inherits her grandmother\'s peculiar profession: mapping the journeys of souls who have lost their way between life and death. Through her work, she discovers family secrets, confronts her own mortality, and learns that some maps lead not to places, but to understanding.',
    tags: ['Magical Realism', 'Family Saga', 'Spiritual Journey', 'Contemporary Fiction']
  }
])

// Computed properties
const currentReview = computed(() => reviews.value[currentReviewIndex.value])
const currentBook = computed(() => {
  const bookId = currentReview.value.bookId
  return books.value.find(book => book.id === bookId) || books.value[0]
})

const isCurrentReviewBookmarked = computed(() => 
  bookmarkedReviews.value.has(currentReview.value.id)
)

// Methods
const nextReview = () => {
  if (currentReviewIndex.value < reviews.value.length - 1) {
    currentReviewIndex.value++
  }
}

const previousReview = () => {
  if (currentReviewIndex.value > 0) {
    currentReviewIndex.value--
  }
}

const toggleBookmark = () => {
  const reviewId = currentReview.value.id
  if (bookmarkedReviews.value.has(reviewId)) {
    bookmarkedReviews.value.delete(reviewId)
  } else {
    bookmarkedReviews.value.add(reviewId)
    // Trigger sparkle animation
    showSparkles.value = true
    setTimeout(() => {
      showSparkles.value = false
    }, 1000)
  }
}

const onBookmarkHover = () => {
  if (!isCurrentReviewBookmarked.value) {
    showSparkles.value = true
  }
}

const onBookmarkLeave = () => {
  if (!isCurrentReviewBookmarked.value) {
    showSparkles.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

onMounted(() => {
  // Initialize with some bookmarked reviews for demo
  bookmarkedReviews.value.add(1)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Playfair+Display:wght@400;700&display=swap');

.manuscript-review-chamber {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fdfaf3;
  border: 1px solid #d4c7b2;
  border-radius: 12px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
  font-family: 'Merriweather', serif;
  color: #3b2f2f;
  position: relative;
  overflow: hidden;
}

.manuscript-review-chamber::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle, rgba(253, 250, 243, 0.9) 0%, rgba(240, 235, 220, 0.9) 100%);
  opacity: 0.8;
  pointer-events: none;
  z-index: -1;
}

.parchment-scroll-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  min-height: 80vh;
}

/* Left Panel - Book Details */
.tome-details-panel {
  background: #f8f4ed;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c0;
  position: relative;
}

.book-showcase-card {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.book-hero-section {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
  background: linear-gradient(135deg, #ffffff 0%, #f8f4ed 100%);
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid #e8e0d4;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
}

.book-hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(212, 163, 115, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(50%, -50%);
}

.illuminated-cover-section {
  position: relative;
  flex-shrink: 0;
}

.featured-tome-cover {
  width: 160px;
  height: 240px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
  transition: transform 0.4s ease, box-shadow 0.4s ease;
}

.cover-glow {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  background: linear-gradient(45deg, rgba(212, 163, 115, 0.3), rgba(141, 110, 99, 0.3));
  border-radius: 12px;
  opacity: 0;
  transition: opacity 0.4s ease;
  z-index: -1;
}

.featured-tome-cover:hover + .cover-ornament + .cover-glow,
.illuminated-cover-section:hover .cover-glow {
  opacity: 1;
}

.book-primary-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1rem;
}

.tome-grand-title {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  font-weight: 700;
  color: #4e342e;
  margin: 0;
  line-height: 1.2;
}

.tome-author-inscription {
  font-family: 'Merriweather', serif;
  font-size: 1.2rem;
  color: #6d5448;
  margin: 0;
  font-style: italic;
}

.quick-details-ribbon {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.detail-badge {
  background: #e0d4c0;
  color: #5a4b41;
  padding: 0.4rem 0.8rem;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid #d4c7b2;
}

.book-detailed-section {
  animation: bookDetailsSlideIn 0.8s ease-out;
}

@keyframes bookDetailsSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.cover-ornament {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 30px;
  height: 30px;
  background: radial-gradient(circle, #d4a373, #8d6e63);
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.tome-manuscript-details {
  width: 100%;
}

.celestial-rating-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  margin-bottom: 2rem;
}

.golden-stars {
  color: #e6b800;
  font-size: 1.8rem;
  letter-spacing: 0.1em;
}

.rating-whispers {
  font-size: 1rem;
  color: #8c7f73;
}

.tome-essence-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e8e0d4;
}

.detail-scroll {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.8rem;
  border-radius: 6px;
  background: #fdfaf3;
  transition: transform 0.2s ease;
}

.detail-scroll:hover {
  transform: translateY(-2px);
}

.detail-label {
  font-size: 0.9rem;
  color: #8c7f73;
  font-weight: 600;
  margin-bottom: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 1.1rem;
  color: #4e342e;
  font-weight: 700;
}

.tome-synopsis {
  margin-bottom: 2rem;
  text-align: left;
}

.synopsis-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  color: #5a4b41;
  margin-bottom: 1rem;
  text-align: center;
  position: relative;
}

.synopsis-title::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #d4a373, transparent);
}

.synopsis-text {
  font-size: 1rem;
  line-height: 1.7;
  color: #3b2f2f;
  text-align: justify;
}

.genre-seals-collection {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  justify-content: center;
}

.genre-seal-tag {
  background: #e0d4c0;
  color: #5a4b41;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid #d4c7b2;
  transition: all 0.3s ease;
}

.genre-seal-tag:hover {
  background: #d4c7b2;
  transform: translateY(-2px);
}

/* Right Panel - Review */
.review-manuscript-panel {
  background: #f0ebe0;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border: 1px solid #d4c7b2;
  display: flex;
  flex-direction: column;
}

.review-parchment-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.review-header-scroll {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px dashed #c0b29b;
}

.review-chamber-title {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  color: #4e342e;
  font-weight: 700;
}

.review-navigation-quills {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-quill-button {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.8rem 1.5rem;
  border: 2px solid #d4a373;
  border-radius: 25px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f4ed 100%);
  color: #5a4b41;
  cursor: pointer;
  transition: all 0.4s ease;
  font-family: 'Merriweather', serif;
  font-size: 0.9rem;
  font-weight: 600;
  position: relative;
  overflow: hidden;
}

.nav-quill-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(212, 163, 115, 0.3), transparent);
  transition: left 0.6s ease;
}

.nav-quill-button:hover:not(.quill-disabled)::before {
  left: 100%;
}

.nav-quill-button:hover:not(.quill-disabled) {
  background: linear-gradient(135deg, #f8f4ed 0%, #e8e0d4 100%);
  border-color: #8d6e63;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.quill-feather {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.quill-shaft {
  width: 20px;
  height: 2px;
  background: linear-gradient(90deg, #8d6e63, #d4a373);
  border-radius: 1px;
}

.quill-tip {
  font-size: 1.2rem;
  font-weight: bold;
  color: #8d6e63;
}

.nav-quill-button.quill-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #c0b29b;
  color: #c0b29b;
}

.nav-quill-button.quill-disabled .quill-shaft {
  background: #c0b29b;
}

.nav-quill-button.quill-disabled .quill-tip {
  color: #c0b29b;
}

.review-counter-ornate {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #f0ebe0 0%, #e8e0d4 100%);
  border-radius: 20px;
  border: 1px solid #d4c7b2;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
}

.counter-decoration {
  color: #d4a373;
  font-size: 1.2rem;
}

.review-counter {
  font-size: 1rem;
  color: #6d5448;
  font-weight: 700;
  font-family: 'Playfair Display', serif;
  min-width: 80px;
  text-align: center;
}

.nav-quill-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #8d6e63;
  background: #ffffff;
  color: #8d6e63;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-quill-button:hover:not(.quill-disabled) {
  background: #8d6e63;
  color: #ffffff;
  transform: scale(1.1);
}

.nav-quill-button.quill-disabled {
  opacity: 0.4;
  cursor: not-allowed;
  border-color: #c0b29b;
  color: #c0b29b;
}

.review-counter {
  font-size: 1rem;
  color: #6d5448;
  font-weight: 600;
  min-width: 80px;
  text-align: center;
}

.review-content-scroll {
  flex: 1;
  animation: reviewSlideIn 0.6s ease-out;
}

@keyframes reviewSlideIn {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.reviewer-seal {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e8e0d4;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.reviewer-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #d4a373;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.reviewer-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.reviewer-inscription {
  flex: 1;
}

.reviewer-name {
  font-family: 'Playfair Display', serif;
  font-size: 1.3rem;
  color: #4e342e;
  margin-bottom: 0.3rem;
  font-weight: 700;
}

.reviewer-title {
  font-size: 0.95rem;
  color: #8c7f73;
  margin-bottom: 0.8rem;
  font-style: italic;
}

.review-celestial-rating {
  display: flex;
  align-items: center;
}

.review-stars {
  color: #e6b800;
  font-size: 1.3rem;
  letter-spacing: 0.05em;
}

.review-manuscript-text {
  position: relative;
  padding: 2rem;
  background: #fdfaf3;
  border-radius: 12px;
  border: 1px solid #e8e0d4;
  margin-bottom: 2rem;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
}

.opening-quote-mark,
.closing-quote-mark {
  position: absolute;
  font-family: 'Playfair Display', serif;
  font-size: 4rem;
  color: rgba(212, 163, 115, 0.3);
  font-weight: 700;
  line-height: 1;
}

.opening-quote-mark {
  top: 0.5rem;
  left: 1rem;
}

.closing-quote-mark {
  bottom: 0.5rem;
  right: 1rem;
}

.review-text {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #3b2f2f;
  text-align: justify;
  position: relative;
  z-index: 1;
  margin: 1rem 0;
}

.review-metadata-scroll {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #e8e0d4;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.review-date,
.review-helpful {
  font-size: 0.9rem;
  color: #6d5448;
  font-style: italic;
}

.bookmark-chamber {
  margin-top: auto;
  display: flex;
  justify-content: center;
}

.bookmark-quill-button {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.2rem 2rem;
  background: #ffffff;
  border: 2px solid #d4a373;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.4s ease;
  font-family: 'Merriweather', serif;
  font-size: 1rem;
  color: #5a4b41;
  position: relative;
  overflow: hidden;
}

.bookmark-quill-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(212, 163, 115, 0.2), transparent);
  transition: left 0.6s ease;
}

.bookmark-quill-button:hover::before {
  left: 100%;
}

.bookmark-quill-button:hover {
  background: #f8f4ed;
  border-color: #8d6e63;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.bookmark-quill-button.is-bookmarked {
  background: #8d6e63;
  color: #ffffff;
  border-color: #6d5448;
  box-shadow: 0 6px 18px rgba(141, 110, 99, 0.4);
}

.bookmark-quill-button.is-bookmarked:hover {
  background: #6d5448;
  transform: translateY(-3px) scale(1.05);
}

.bookmark-icon-container {
  position: relative;
  display: flex;
  align-items: center;
}

.bookmark-icon {
  font-size: 1.5rem;
  transition: transform 0.3s ease;
}

.bookmark-quill-button:hover .bookmark-icon {
  transform: rotate(10deg) scale(1.1);
}

.bookmark-sparkles {
  position: absolute;
  top: -10px;
  right: -10px;
  font-size: 1rem;
  animation: sparkleFloat 1s ease-in-out infinite;
}

@keyframes sparkleFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 1; }
  50% { transform: translateY(-8px) rotate(180deg); opacity: 0.7; }
}

.bookmark-text {
  font-weight: 600;
  letter-spacing: 0.02em;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .parchment-scroll-container {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .tome-details-panel,
  .review-manuscript-panel {
    padding: 2rem;
  }
  
  .tome-essence-details {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .manuscript-review-chamber {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .tome-grand-title {
    font-size: 1.8rem;
  }
  
  .review-chamber-title {
    font-size: 1.6rem;
  }
  
  .reviewer-seal {
    flex-direction: column;
    text-align: center;
  }
  
  .review-metadata-scroll {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  .bookmark-quill-button {
    padding: 1rem 1.5rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .featured-tome-cover {
    width: 180px;
    height: 260px;
  }
  
  .review-navigation-quills {
    gap: 0.5rem;
  }
  
  .nav-quill-button {
    width: 35px;
    height: 35px;
    font-size: 1.2rem;
  }
  
  .review-counter {
    font-size: 0.9rem;
    min-width: 70px;
  }
}
</style>
<template>
  <div class="manuscript-review-chamber">
    <!-- Main Content Area -->
    <div class="parchment-scroll-container">
      <!-- Left Panel: Book Details -->
      <div class="tome-details-panel">
        <div class="book-showcase-card">
          <div class="book-hero-section">
            <div class="illuminated-cover-section">
              <img :src="currentBook.coverImage" :alt="currentBook.title" class="featured-tome-cover" />
              <div class="cover-ornament"></div>
              <div class="cover-glow"></div>
            </div>
            
            <div class="book-primary-info">
              <h1 class="tome-grand-title">{{ currentBook.title }}</h1>
              <h2 class="tome-author-inscription">{{ currentBook.author }}</h2>
              
              <div class="celestial-rating-display">
                <span class="golden-stars">{{ '★'.repeat(Math.round(currentBook.rating)) }}{{ '☆'.repeat(5 - Math.round(currentBook.rating)) }}</span>
                <span class="rating-whispers">({{ currentBook.rating }} from {{ currentBook.totalRatings }} souls)</span>
              </div>
              
              <div class="quick-details-ribbon">
                <span class="detail-badge">{{ currentBook.genre }}</span>
                <span class="detail-badge">{{ currentBook.publishYear }}</span>
                <span class="detail-badge">${{ currentBook.price }}</span>
              </div>
            </div>
          </div>

          <div class="book-detailed-section" :key="currentBook.id">
            <div class="tome-essence-details">
              <div class="detail-scroll">
                <span class="detail-label">Genre:</span>
                <span class="detail-value">{{ currentBook.genre }}</span>
              </div>
              <div class="detail-scroll">
                <span class="detail-label">Published:</span>
                <span class="detail-value">{{ currentBook.publishYear }}</span>
              </div>
              <div class="detail-scroll">
                <span class="detail-label">Pages:</span>
                <span class="detail-value">{{ currentBook.pages }}</span>
              </div>
              <div class="detail-scroll">
                <span class="detail-label">Price:</span>
                <span class="detail-value">${{ currentBook.price }}</span>
              </div>
            </div>
            
            <div class="tome-synopsis">
              <h3 class="synopsis-title">Synopsis</h3>
              <p class="synopsis-text">{{ currentBook.description }}</p>
            </div>
            
            <div class="genre-seals-collection">
              <span v-for="tag in currentBook.tags" :key="tag" class="genre-seal-tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Book Review -->
      <div class="review-manuscript-panel">
        <div class="review-parchment-card">
          <div class="review-header-scroll">
            <h2 class="review-chamber-title">Scholarly Discourse</h2>
            <div class="review-navigation-quills">
              <button 
                @click="previousReview" 
                :disabled="currentReviewIndex === 0"
                class="nav-quill-button prev-quill"
                :class="{ 'quill-disabled': currentReviewIndex === 0 }"
              >
                <div class="quill-feather">
                  <span class="quill-shaft"></span>
                  <span class="quill-tip">‹</span>
                </div>
                <span class="quill-label">Previous</span>
              </button>
              
              <div class="review-counter-ornate">
                <span class="counter-decoration">❦</span>
                <span class="review-counter">{{ currentReviewIndex + 1 }} of {{ reviews.length }}</span>
                <span class="counter-decoration">❦</span>
              </div>
              
              <button 
                @click="nextReview" 
                :disabled="currentReviewIndex === reviews.length - 1"
                class="nav-quill-button next-quill"
                :class="{ 'quill-disabled': currentReviewIndex === reviews.length - 1 }"
              >
                <span class="quill-label">Next</span>
                <div class="quill-feather">
                  <span class="quill-shaft"></span>
                  <span class="quill-tip">›</span>
                </div>
              </button>
            </div>
          </div>

          <div class="review-content-scroll" :key="currentReview.id">
            <div class="reviewer-seal">
              <div class="reviewer-avatar">
                <img :src="currentReview.reviewerAvatar" :alt="currentReview.reviewerName" />
              </div>
              <div class="reviewer-inscription">
                <h4 class="reviewer-name">{{ currentReview.reviewerName }}</h4>
                <p class="reviewer-title">{{ currentReview.reviewerTitle }}</p>
                <div class="review-celestial-rating">
                  <span class="review-stars">{{ '★'.repeat(currentReview.rating) }}{{ '☆'.repeat(5 - currentReview.rating) }}</span>
                </div>
              </div>
            </div>

            <div class="review-manuscript-text">
              <div class="opening-quote-mark">"</div>
              <p class="review-text">{{ currentReview.reviewText }}</p>
              <div class="closing-quote-mark">"</div>
            </div>

            <div class="review-metadata-scroll">
              <span class="review-date">Inscribed on {{ formatDate(currentReview.date) }}</span>
              <span class="review-helpful">{{ currentReview.helpfulCount }} found this enlightening</span>
            </div>
          </div>

          <!-- Bookmark Button -->
          <div class="bookmark-chamber">
            <button 
              @click="toggleBookmark"
              class="bookmark-quill-button"
              :class="{ 'is-bookmarked': isCurrentReviewBookmarked }"
              @mouseenter="onBookmarkHover"
              @mouseleave="onBookmarkLeave"
            >
              <div class="bookmark-icon-container">
                <span class="bookmark-icon">🔖</span>
                <span class="bookmark-sparkles" v-if="showSparkles">✨</span>
              </div>
              <span class="bookmark-text">
                {{ isCurrentReviewBookmarked ? 'Preserved in thy Collection' : 'Preserve this Wisdom' }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Reactive data
const currentReviewIndex = ref(0)
const bookmarkedReviews = ref(new Set())
const showSparkles = ref(false)

// Mock data for reviews and books
const reviews = ref([
  {
    id: 1,
    bookId: 'book1',
    reviewerName: 'Eleanor Whitmore',
    reviewerTitle: 'Professor of Classical Literature',
    reviewerAvatar: '/placeholder.svg?height=60&width=60',
    rating: 5,
    reviewText: 'This masterpiece transcends the boundaries of conventional storytelling, weaving together threads of philosophy, adventure, and profound human insight. The author\'s prose flows like liquid gold, each sentence carefully crafted to resonate with the reader\'s soul. I found myself completely immersed in this world, unable to put the book down until the very last page. The character development is extraordinary, and the themes explored are both timeless and remarkably relevant to our modern age.',
    date: '2024-12-15',
    helpfulCount: 127
  },
  {
    id: 2,
    bookId: 'book2',
    reviewerName: 'Marcus Thornfield',
    reviewerTitle: 'Literary Critic & Author',
    reviewerAvatar: '/placeholder.svg?height=60&width=60',
    rating: 4,
    reviewText: 'A compelling narrative that challenges readers to question their assumptions about society and human nature. While the pacing occasionally falters in the middle chapters, the author\'s brilliant use of symbolism and metaphor more than compensates for any structural weaknesses. The dialogue is sharp and authentic, bringing each character to vivid life. This is the kind of book that stays with you long after reading, prompting deep reflection and discussion.',
    date: '2024-12-10',
    helpfulCount: 89
  },
  {
    id: 3,
    bookId: 'book3',
    reviewerName: 'Dr. Sophia Chen',
    reviewerTitle: 'Philosophy Department Head',
    reviewerAvatar: '/placeholder.svg?height=60&width=60',
    rating: 5,
    reviewText: 'An intellectual tour de force that seamlessly blends entertainment with profound philosophical inquiry. The author demonstrates remarkable erudition while maintaining accessibility for general readers. Each chapter builds upon the last, creating a crescendo of understanding that culminates in a deeply satisfying conclusion. The exploration of moral ambiguity and the nature of truth is handled with exceptional nuance and sophistication.',
    date: '2024-12-08',
    helpfulCount: 156
  }
])

const books = ref([
  {
    id: 'book1',
    title: 'The Luminous Codex of Eternal Wisdom',
    author: 'Arabella Nightingale',
    coverImage: '/placeholder.svg?height=400&width=280',
    rating: 4.8,
    totalRatings: 2847,
    genre: 'Philosophical Fiction',
    publishYear: 2023,
    pages: 487,
    price: 24.99,
    description: 'A profound exploration of human consciousness and the nature of reality, told through the journey of a young scholar who discovers an ancient manuscript that challenges everything she believes about existence. This luminous work weaves together elements of mysticism, science, and philosophy in a narrative that is both intellectually stimulating and emotionally resonant.',
    tags: ['Philosophy', 'Mystery', 'Literary Fiction', 'Metaphysical']
  },
  {
    id: 'book2',
    title: 'Shadows of the Forgotten Realm',
    author: 'Cornelius Blackwood',
    coverImage: '/placeholder.svg?height=400&width=280',
    rating: 4.3,
    totalRatings: 1923,
    genre: 'Dark Fantasy',
    publishYear: 2022,
    pages: 623,
    price: 27.50,
    description: 'In a world where magic has been forgotten and technology reigns supreme, a young archaeologist uncovers artifacts that suggest a different history than what has been recorded. As she delves deeper into the mystery, she discovers that some knowledge was hidden for good reason, and that the shadows of the past are not as dormant as they appear.',
    tags: ['Fantasy', 'Adventure', 'Archaeological Mystery', 'Dark Magic']
  },
  {
    id: 'book3',
    title: 'The Cartographer of Lost Souls',
    author: 'Isadora Moonwhisper',
    coverImage: '/placeholder.svg?height=400&width=280',
    rating: 4.9,
    totalRatings: 3156,
    genre: 'Magical Realism',
    publishYear: 2024,
    pages: 398,
    price: 22.95,
    description: 'A haunting and beautiful tale of a woman who inherits her grandmother\'s peculiar profession: mapping the journeys of souls who have lost their way between life and death. Through her work, she discovers family secrets, confronts her own mortality, and learns that some maps lead not to places, but to understanding.',
    tags: ['Magical Realism', 'Family Saga', 'Spiritual Journey', 'Contemporary Fiction']
  }
])

// Computed properties
const currentReview = computed(() => reviews.value[currentReviewIndex.value])
const currentBook = computed(() => {
  const bookId = currentReview.value.bookId
  return books.value.find(book => book.id === bookId) || books.value[0]
})

const isCurrentReviewBookmarked = computed(() => 
  bookmarkedReviews.value.has(currentReview.value.id)
)

// Methods
const nextReview = () => {
  if (currentReviewIndex.value < reviews.value.length - 1) {
    currentReviewIndex.value++
  }
}

const previousReview = () => {
  if (currentReviewIndex.value > 0) {
    currentReviewIndex.value--
  }
}

const toggleBookmark = () => {
  const reviewId = currentReview.value.id
  if (bookmarkedReviews.value.has(reviewId)) {
    bookmarkedReviews.value.delete(reviewId)
  } else {
    bookmarkedReviews.value.add(reviewId)
    // Trigger sparkle animation
    showSparkles.value = true
    setTimeout(() => {
      showSparkles.value = false
    }, 1000)
  }
}

const onBookmarkHover = () => {
  if (!isCurrentReviewBookmarked.value) {
    showSparkles.value = true
  }
}

const onBookmarkLeave = () => {
  if (!isCurrentReviewBookmarked.value) {
    showSparkles.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

onMounted(() => {
  // Initialize with some bookmarked reviews for demo
  bookmarkedReviews.value.add(1)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Playfair+Display:wght@400;700&display=swap');

.manuscript-review-chamber {
  max-width: 1400px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fdfaf3;
  border: 1px solid #d4c7b2;
  border-radius: 12px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
  font-family: 'Merriweather', serif;
  color: #3b2f2f;
  position: relative;
  overflow: hidden;
}

.manuscript-review-chamber::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle, rgba(253, 250, 243, 0.9) 0%, rgba(240, 235, 220, 0.9) 100%);
  opacity: 0.8;
  pointer-events: none;
  z-index: -1;
}

.parchment-scroll-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  min-height: 80vh;
}

/* Left Panel - Book Details */
.tome-details-panel {
  background: #f8f4ed;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0d4c0;
  position: relative;
}

.book-showcase-card {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.book-hero-section {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
  background: linear-gradient(135deg, #ffffff 0%, #f8f4ed 100%);
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid #e8e0d4;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
}

.book-hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(212, 163, 115, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(50%, -50%);
}

.illuminated-cover-section {
  position: relative;
  flex-shrink: 0;
}

.featured-tome-cover {
  width: 160px;
  height: 240px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
  transition: transform 0.4s ease, box-shadow 0.4s ease;
}

.cover-glow {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  background: linear-gradient(45deg, rgba(212, 163, 115, 0.3), rgba(141, 110, 99, 0.3));
  border-radius: 12px;
  opacity: 0;
  transition: opacity 0.4s ease;
  z-index: -1;
}

.featured-tome-cover:hover + .cover-ornament + .cover-glow,
.illuminated-cover-section:hover .cover-glow {
  opacity: 1;
}

.book-primary-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1rem;
}

.tome-grand-title {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  font-weight: 700;
  color: #4e342e;
  margin: 0;
  line-height: 1.2;
}

.tome-author-inscription {
  font-family: 'Merriweather', serif;
  font-size: 1.2rem;
  color: #6d5448;
  margin: 0;
  font-style: italic;
}

.quick-details-ribbon {
  display: flex;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.detail-badge {
  background: #e0d4c0;
  color: #5a4b41;
  padding: 0.4rem 0.8rem;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid #d4c7b2;
}

.book-detailed-section {
  animation: bookDetailsSlideIn 0.8s ease-out;
}

@keyframes bookDetailsSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.cover-ornament {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 30px;
  height: 30px;
  background: radial-gradient(circle, #d4a373, #8d6e63);
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.tome-manuscript-details {
  width: 100%;
}

.celestial-rating-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  margin-bottom: 2rem;
}

.golden-stars {
  color: #e6b800;
  font-size: 1.8rem;
  letter-spacing: 0.1em;
}

.rating-whispers {
  font-size: 1rem;
  color: #8c7f73;
}

.tome-essence-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e8e0d4;
}

.detail-scroll {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.8rem;
  border-radius: 6px;
  background: #fdfaf3;
  transition: transform 0.2s ease;
}

.detail-scroll:hover {
  transform: translateY(-2px);
}

.detail-label {
  font-size: 0.9rem;
  color: #8c7f73;
  font-weight: 600;
  margin-bottom: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 1.1rem;
  color: #4e342e;
  font-weight: 700;
}

.tome-synopsis {
  margin-bottom: 2rem;
  text-align: left;
}

.synopsis-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  color: #5a4b41;
  margin-bottom: 1rem;
  text-align: center;
  position: relative;
}

.synopsis-title::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #d4a373, transparent);
}

.synopsis-text {
  font-size: 1rem;
  line-height: 1.7;
  color: #3b2f2f;
  text-align: justify;
}

.genre-seals-collection {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  justify-content: center;
}

.genre-seal-tag {
  background: #e0d4c0;
  color: #5a4b41;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid #d4c7b2;
  transition: all 0.3s ease;
}

.genre-seal-tag:hover {
  background: #d4c7b2;
  transform: translateY(-2px);
}

/* Right Panel - Review */
.review-manuscript-panel {
  background: #f0ebe0;
  border-radius: 12px;
  padding: 2.5rem;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border: 1px solid #d4c7b2;
  display: flex;
  flex-direction: column;
}

.review-parchment-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.review-header-scroll {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px dashed #c0b29b;
}

.review-chamber-title {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  color: #4e342e;
  font-weight: 700;
}

.review-navigation-quills {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-quill-button {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.8rem 1.5rem;
  border: 2px solid #d4a373;
  border-radius: 25px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f4ed 100%);
  color: #5a4b41;
  cursor: pointer;
  transition: all 0.4s ease;
  font-family: 'Merriweather', serif;
  font-size: 0.9rem;
  font-weight: 600;
  position: relative;
  overflow: hidden;
}

.nav-quill-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(212, 163, 115, 0.3), transparent);
  transition: left 0.6s ease;
}

.nav-quill-button:hover:not(.quill-disabled)::before {
  left: 100%;
}

.nav-quill-button:hover:not(.quill-disabled) {
  background: linear-gradient(135deg, #f8f4ed 0%, #e8e0d4 100%);
  border-color: #8d6e63;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.quill-feather {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.quill-shaft {
  width: 20px;
  height: 2px;
  background: linear-gradient(90deg, #8d6e63, #d4a373);
  border-radius: 1px;
}

.quill-tip {
  font-size: 1.2rem;
  font-weight: bold;
  color: #8d6e63;
}

.nav-quill-button.quill-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: #c0b29b;
  color: #c0b29b;
}

.nav-quill-button.quill-disabled .quill-shaft {
  background: #c0b29b;
}

.nav-quill-button.quill-disabled .quill-tip {
  color: #c0b29b;
}

.review-counter-ornate {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #f0ebe0 0%, #e8e0d4 100%);
  border-radius: 20px;
  border: 1px solid #d4c7b2;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
}

.counter-decoration {
  color: #d4a373;
  font-size: 1.2rem;
}

.review-counter {
  font-size: 1rem;
  color: #6d5448;
  font-weight: 700;
  font-family: 'Playfair Display', serif;
  min-width: 80px;
  text-align: center;
}

.nav-quill-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #8d6e63;
  background: #ffffff;
  color: #8d6e63;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-quill-button:hover:not(.quill-disabled) {
  background: #8d6e63;
  color: #ffffff;
  transform: scale(1.1);
}

.nav-quill-button.quill-disabled {
  opacity: 0.4;
  cursor: not-allowed;
  border-color: #c0b29b;
  color: #c0b29b;
}

.review-counter {
  font-size: 1rem;
  color: #6d5448;
  font-weight: 600;
  min-width: 80px;
  text-align: center;
}

.review-content-scroll {
  flex: 1;
  animation: reviewSlideIn 0.6s ease-out;
}

@keyframes reviewSlideIn {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.reviewer-seal {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e8e0d4;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.reviewer-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #d4a373;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.reviewer-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.reviewer-inscription {
  flex: 1;
}

.reviewer-name {
  font-family: 'Playfair Display', serif;
  font-size: 1.3rem;
  color: #4e342e;
  margin-bottom: 0.3rem;
  font-weight: 700;
}

.reviewer-title {
  font-size: 0.95rem;
  color: #8c7f73;
  margin-bottom: 0.8rem;
  font-style: italic;
}

.review-celestial-rating {
  display: flex;
  align-items: center;
}

.review-stars {
  color: #e6b800;
  font-size: 1.3rem;
  letter-spacing: 0.05em;
}

.review-manuscript-text {
  position: relative;
  padding: 2rem;
  background: #fdfaf3;
  border-radius: 12px;
  border: 1px solid #e8e0d4;
  margin-bottom: 2rem;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
}

.opening-quote-mark,
.closing-quote-mark {
  position: absolute;
  font-family: 'Playfair Display', serif;
  font-size: 4rem;
  color: rgba(212, 163, 115, 0.3);
  font-weight: 700;
  line-height: 1;
}

.opening-quote-mark {
  top: 0.5rem;
  left: 1rem;
}

.closing-quote-mark {
  bottom: 0.5rem;
  right: 1rem;
}

.review-text {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #3b2f2f;
  text-align: justify;
  position: relative;
  z-index: 1;
  margin: 1rem 0;
}

.review-metadata-scroll {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #e8e0d4;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.review-date,
.review-helpful {
  font-size: 0.9rem;
  color: #6d5448;
  font-style: italic;
}

.bookmark-chamber {
  margin-top: auto;
  display: flex;
  justify-content: center;
}

.bookmark-quill-button {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.2rem 2rem;
  background: #ffffff;
  border: 2px solid #d4a373;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.4s ease;
  font-family: 'Merriweather', serif;
  font-size: 1rem;
  color: #5a4b41;
  position: relative;
  overflow: hidden;
}

.bookmark-quill-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(212, 163, 115, 0.2), transparent);
  transition: left 0.6s ease;
}

.bookmark-quill-button:hover::before {
  left: 100%;
}

.bookmark-quill-button:hover {
  background: #f8f4ed;
  border-color: #8d6e63;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.bookmark-quill-button.is-bookmarked {
  background: #8d6e63;
  color: #ffffff;
  border-color: #6d5448;
  box-shadow: 0 6px 18px rgba(141, 110, 99, 0.4);
}

.bookmark-quill-button.is-bookmarked:hover {
  background: #6d5448;
  transform: translateY(-3px) scale(1.05);
}

.bookmark-icon-container {
  position: relative;
  display: flex;
  align-items: center;
}

.bookmark-icon {
  font-size: 1.5rem;
  transition: transform 0.3s ease;
}

.bookmark-quill-button:hover .bookmark-icon {
  transform: rotate(10deg) scale(1.1);
}

.bookmark-sparkles {
  position: absolute;
  top: -10px;
  right: -10px;
  font-size: 1rem;
  animation: sparkleFloat 1s ease-in-out infinite;
}

@keyframes sparkleFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 1; }
  50% { transform: translateY(-8px) rotate(180deg); opacity: 0.7; }
}

.bookmark-text {
  font-weight: 600;
  letter-spacing: 0.02em;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .parchment-scroll-container {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .tome-details-panel,
  .review-manuscript-panel {
    padding: 2rem;
  }
  
  .tome-essence-details {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .manuscript-review-chamber {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .tome-grand-title {
    font-size: 1.8rem;
  }
  
  .review-chamber-title {
    font-size: 1.6rem;
  }
  
  .reviewer-seal {
    flex-direction: column;
    text-align: center;
  }
  
  .review-metadata-scroll {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  .bookmark-quill-button {
    padding: 1rem 1.5rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .featured-tome-cover {
    width: 180px;
    height: 260px;
  }
  
  .review-navigation-quills {
    gap: 0.5rem;
  }
  
  .nav-quill-button {
    width: 35px;
    height: 35px;
    font-size: 1.2rem;
  }
  
  .review-counter {
    font-size: 0.9rem;
    min-width: 70px;
  }
}
</style>