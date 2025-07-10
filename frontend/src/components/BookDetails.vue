<!-- 书籍细节信息页面 -->
<template>
  <div class="ancient-scroll-page" v-if="book">
    <div class="main-parchment-folio">
      <div class="tome-unveiling-header">
        <div class="tome-illumination">
          <img :src="book.coverImg" :alt="book.title" class="tome-cover-illustration" />
        </div>
        <div class="tome-essential-data">
          <h1 class="tome-grand-title">{{ book.title }}</h1>
          <h2 v-if="book.series" class="tome-series-chapter">A Volume in The {{ book.series }} Chronicle</h2>
          <p class="tome-scribe">Penned by {{ book.author }}</p>

          <div class="celestial-judgement">
            <span class="stars-bestowed">{{ '★'.repeat(Math.round(book.rating)) }}{{ '☆'.repeat(5 -
              Math.round(book.rating))
              }}</span>
            <span class="whispers-of-appraisal">({{ book.rating }} from {{ book.numRatings }} Judgements)</span>
          </div>

          <div class="tome-interactive-actions">
            <button @click="toggleLike" :class="{ 'action-button': true, 'liked': isLiked }">
              <span class="icon">{{ isLiked ? '❤️' : '🤍' }}</span> {{ isLiked ? 'Liked' : 'Like' }} ({{ likeCount }})
            </button>
            <button @click="toggleCollect" :class="{ 'action-button': true, 'collected': isCollected }">
              <span class="icon">{{ isCollected ? '✅' : '➕' }}</span> {{ isCollected ? 'Collected' : 'Collect' }}
            </button>
            <button v-if="book && book.epubUrl" @click="readOnline" class="action-button">
              <span class="icon">📖</span> Read Online
            </button>
          </div>
          <div class="tome-provenance-details-grid">
            <div class="detail-item"><strong>First Inscribed:</strong> {{ book.firstPublishDate || 'Unknown' }}</div>
            <div class="detail-item"><strong>Published:</strong> {{ book.publishDate }}</div>
            <div class="detail-item"><strong>Folios:</strong> {{ book.pages }}</div>
            <div class="detail-item"><strong>Appraisal:</strong> ${{ book.price }}</div>
            <div class="detail-item" v-if="book.language"><strong>Tongue:</strong> {{ book.language }}</div>
            <div class="detail-item" v-if="book.isbn"><strong>Cipher (ISBN):</strong> {{ book.isbn }}</div>
            <div class="detail-item" v-if="book.bookFormat"><strong>Form:</strong> {{ book.bookFormat }}</div>
            <div class="detail-item" v-if="book.edition"><strong>Edition:</strong> {{ book.edition }}</div>
            <div class="detail-item" v-if="book.publisher"><strong>Printer:</strong> {{ book.publisher }}</div>
            <div class="detail-item" v-if="book.bbeScore"><strong>BBE Oracle Score:</strong> {{ book.bbeScore }} (from
              {{
                book.bbeVotes }} Voices)</div>
          </div>

          <div class="scholarly-genres-seals">
            <span v-for="genre in book.genres" :key="genre" class="genre-crest">{{ genre }}</span>
          </div>
        </div>
      </div>

      <div class="tome-narrative-summary">
        <h3 class="section-heading">The Chronicle's Essence</h3>
        <p class="summary-parchment">
          {{ displayDescription }}
          <span v-if="shouldShowDescriptionToggle" @click="toggleDescription" class="toggle-text-button">
            {{ showFullDescription ? 'Show Less' : 'Show More' }}
          </span>
        </p>
      </div>

      <div class="tome-additional-annotations">
        <div v-if="book.characters && book.characters.length > 0">
          <h3 class="section-heading">Notable Figures Within</h3>
          <div class="characters-of-note">
            <span v-for="character in book.characters" :key="character" class="character-sigil">{{ character
              }}</span>
          </div>
        </div>

        <div v-if="book.setting && book.setting.length > 0">
          <h3 class="section-heading">Realms & Locales Described</h3>
          <div class="settings-of-the-tale">
            <span v-for="loc in book.setting" :key="loc" class="setting-marker">{{ loc }}</span>
          </div>
        </div>

        <div v-if="book.awards && book.awards.length > 0">
          <h3 class="section-heading">Laurels & Distinctions Awarded</h3>
          <ul class="laurels-list">
            <li v-for="(award, index) in displayAwards" :key="index">{{ award }}</li>
            <li v-if="shouldShowAwardsToggle" class="toggle-list-item">
              <a href="#" @click.prevent="toggleAwards" class="toggle-text-button">
                {{ showAllAwards ? 'Show Less' : 'Show More' }}
              </a>
            </li>
          </ul>
        </div>

        <div v-if="book.likedPercent || (book.ratingsByStars && Object.keys(book.ratingsByStars).length > 0)"
          class="readership-stats-group">
          <h3 class="section-heading">Affection & Distribution of Critiques</h3>
          <div class="stats-content-flex">
            <div v-if="book.likedPercent" class="affection-measure-container">
              <p class="affection-measure">{{ book.likedPercent }}% of Readers Hold This Tome Dearly.</p>
            </div>

            <div v-if="book.ratingsByStars && Object.keys(book.ratingsByStars).length > 0"
              class="critique-distribution">
              <div v-for="(count, star) in book.ratingsByStars" :key="star" class="star-critique-row">
                <span>{{ star }} Stars:</span>
                <div class="star-bar-scroll-container">
                  <div class="star-bar-illumination" :style="{ width: (count / book.numRatings * 100) + '%' }"></div>
                </div>
                <span>({{ count }})</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="tome-reviews-section">
        <h3 class="section-heading">Reader's Reflections</h3>

        <div class="review-submission-form">
          <h4>Pen Your Own Reflection</h4>
          <textarea v-model="newReviewContent" placeholder="Share your thoughts on this tome..." rows="5"
            class="review-textarea"></textarea>
          <div class="review-rating-input">
            <label for="review-rating">Your Appraisal:</label>
            <select v-model.number="newReviewRating" id="review-rating" class="review-rating-select">
              <option value="0" disabled>Select a rating</option>
              <option v-for="n in 5" :key="n" :value="n">{{ n }} Star{{ n > 1 ? 's' : '' }}</option>
            </select>
          </div>
          <button @click="submitReview" class="submit-review-button">Inscribe Your Review</button>
        </div>

        <div class="existing-reviews-list">
          <p v-if="bookReviews.length === 0" class="no-reviews-message">No reflections penned yet. Be the first!</p>
          <div v-for="review in bookReviews" :key="review.id" class="review-entry">
            <div class="review-header">
              <img :src="review.reviewerAvatarUrl" alt="Reviewer Avatar" class="reviewer-avatar" />
              <span class="reviewer-name">{{ review.reviewerNickname }}</span>
              <span class="review-date">
                {{ review.post_time instanceof Date && !isNaN(review.post_time.getTime())
                  ? review.post_time.toLocaleDateString()
                  : '日期无效' }}
              </span>
              <span class="review-stars">{{ '★'.repeat(review.rating) }}{{ '☆'.repeat(5 - review.rating) }}</span>
              <button v-if="currentUserId === review.userId" @click="deleteReview(review.id)"
                class="delete-review-button">
                Delete
              </button>
            </div>
            <p class="review-content">{{ review.content }}</p>
            <div class="review-actions">
              <button @click="toggleReviewLike(review)"
                :class="{ 'review-action-button': true, 'liked': review.isLikedByCurrentUser }">
                <span class="icon">{{ review.isLikedByCurrentUser ? '❤️' : '🤍' }}</span> Like ({{ review.likeCount }})
              </button>
              <button @click="toggleReviewCollect(review)"
                :class="{ 'review-action-button': true, 'collected': review.isCollectedByCurrentUser }">
                <span class="icon">{{ review.isCollectedByCurrentUser ? '✅' : '➕' }}</span> Collect ({{
                  review.collectCount }})
              </button>
              <button @click="toggleCommentInput(review.id)" class="review-action-button">
                <span class="icon">💬</span> Comments
              </button>
            </div>

            <div v-if="showCommentInput === review.id" class="comments-section">
              <div class="comment-submission-form">
                <textarea v-model="newCommentContent" placeholder="Add your comment..." rows="3"
                  class="comment-textarea"></textarea>
                <button @click="submitComment(review.id)" class="submit-comment-button">Post Comment</button>
              </div>

              <div class="existing-comments-list">
                <p v-if="!commentsByReview[review.id] || commentsByReview[review.id].length === 0"
                  class="no-comments-message">
                  No comments yet. Be the first to comment!
                </p>
                <div v-for="comment in commentsByReview[review.id]" :key="comment.id" class="comment-entry">
                  <div class="comment-header">
                    <img :src="comment.commenterAvatarUrl || 'https://via.placeholder.com/50/CCCCCC/FFFFFF?text=AV'"
                      alt="Commenter Avatar" class="commenter-avatar" />
                    <span class="commenter-name">{{ comment.commenterNickname || comment.userId }}</span>
                    <span class="comment-date">
                      {{ comment.commentTime instanceof Date && !isNaN(comment.commentTime.getTime())
                        ? comment.commentTime.toLocaleDateString()
                        : '日期无效' }}
                    </span>
                    <button v-if="currentUserId === comment.userId" @click="deleteComment(comment.id, review.id)"
                      class="delete-comment-button">Delete</button>
                  </div>
                  <p class="comment-content">{{ comment.content }}</p>
                </div>
                <button v-if="commentsByReview[review.id] && commentsByReview[review.id].length >= commentsPerPage"
                  @click="loadMoreComments(review.id)" class="load-more-comments-button">Load More Comments</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="tome-actions">
        <button @click="goBack" class="return-to-catalogue-button">Return to the Grand Catalogue</button>
      </div>
    </div>

    <div class="scribe-notes-sidebar">
      <div class="oracle-douban-section">
        <div class="sidebar-section-header" @click="toggleDoubanResults">
          <h2 class="sidebar-section-title">Douban Oracle's Prophecies <span class="toggle-rune">{{ showDoubanResults ?
            '▼' : '▶' }}</span></h2>
        </div>
        <transition name="unfurl-scroll">
          <div v-show="showDoubanResults" class="oracle-results-container">
            <ul v-if="doubanSearchResults.length > 0" class="oracle-findings-list">
              <li v-for="(doubanBook, index) in doubanSearchResults" :key="index" class="oracle-finding-item">
                <a :href="doubanBook.link" target="_blank" rel="noopener noreferrer" class="oracle-link">
                  {{ doubanBook.title }}
                </a>
                <span class="douban-oracle-rating" v-if="doubanBook.rating">
                  {{ '★'.repeat(Math.round(doubanBook.rating)) }}{{ '☆'.repeat(5 - Math.round(doubanBook.rating)) }}
                  ({{ doubanBook.rating }})
                </span>
              </li>
            </ul>
            <p v-else-if="searched && doubanSearchResults.length === 0" class="no-oracle-findings">
              The Oracle finds no kindred spirits on Douban.
            </p>
          </div>
        </transition>
      </div>

      ---

      <div class="realtime-recommendations-section">
        <h3 class="sidebar-section-title">实时推荐：为您量身定制的卷轴</h3>
        <p v-if="realtimeRecommendations.length === 0 && !loadingRecommendations" class="no-recommendations-message">
          尚无实时推荐。探索更多书籍以生成个性化推荐！
        </p>
        <p v-else-if="loadingRecommendations" class="loading-message">
          正在为您生成实时推荐...
        </p>
        <ul v-else class="recommendations-list">
          <li v-for="recBook in realtimeRecommendations" :key="recBook.bookId" class="recommendation-item">
            <router-link :to="`/books/${recBook.bookId}`" class="recommendation-link">
              <img :src="recBook.coverImg" :alt="recBook.title" class="recommendation-cover" />
              <div class="recommendation-info">
                <span class="recommendation-title">{{ recBook.title }}</span>
                <span class="recommendation-author">作者: {{ recBook.author }}</span>
              </div>
            </router-link>
          </li>
        </ul>
      </div>

      ---

      <div class="scribe-notes-section">
        <h3 class="sidebar-section-title">Further Recommendations</h3>
        <p class="sidebar-text">更多推荐典籍待您细品...</p>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="scribe-at-work">
    The Scribe is diligently retrieving the Tome's details...
  </div>
  <div v-else class="tome-vanished">
    Alas, this Tome has vanished from our collection.
  </div>
</template>

<script>
import axios from 'axios';
import { trackPageView, trackButtonClick } from '../services/logger.js';

// Helper function to get user data from localStorage
const getParsedUserData = () => {
  const storedUserData = localStorage.getItem('user_data');
  if (storedUserData) {
    try {
      return JSON.parse(storedUserData);
    } catch (e) {
      console.error("Error parsing user_data from localStorage:", e);
      return null;
    }
  }
  return null;
};

export default {
  name: 'BookDetails',
  data() {
    return {
      book: null,
      loading: true,
      doubanSearchResults: [],
      searched: false,
      showDoubanResults: true,
      isLiked: false,
      likeCount: 0,
      isCollected: false,
      bookReviews: [], // 现在存储的是针对这本书的“书评”
      newReviewContent: '', // 用于撰写新书评的内容
      newReviewRating: 0, // 用于撰写新书评的评分
      showFullDescription: false,
      descriptionLimit: 300,
      showAllAwards: false,
      awardsLimit: 3,
      realtimeRecommendations: [],
      loadingRecommendations: false,

      // 评论相关数据属性
      showCommentInput: null, // 用于控制哪个书评的评论输入框显示 (存储 review.id)
      newCommentContent: '', // 存储新评论的内容
      commentsByReview: {}, // 存储每个书评的评论列表，键为 reviewId
      commentsPage: {}, // 存储每个书评当前评论的页码
      commentsPerPage: 5, // 每页显示的评论数量
    };
  },
  computed: {
    currentUserId() {
      const userData = getParsedUserData();
      return userData ? userData.user_id : null;
    },
    getCurrentUserNickname() {
      const userData = getParsedUserData();
      return userData ? (userData.nickname || userData.email || '访客') : '访客';
    },
    getCurrentUserAvatar() {
      const userData = getParsedUserData();
      return userData ? (userData.avatar_url || 'https://via.placeholder.com/50/CCCCCC/FFFFFF?text=AV') : 'https://via.placeholder.com/50/CCCCCC/FFFFFF?text=AV';
    },
    displayDescription() {
      if (!this.book || !this.book.description) return '';
      if (this.showFullDescription || this.book.description.length <= this.descriptionLimit) {
        return this.book.description;
      }
      return this.book.description.substring(0, this.descriptionLimit) + '...';
    },
    shouldShowDescriptionToggle() {
      return this.book && this.book.description && this.book.description.length > this.descriptionLimit;
    },
    displayAwards() {
      if (!this.book || !this.book.awards) return [];
      if (this.showAllAwards || this.book.awards.length <= this.awardsLimit) {
        return this.book.awards;
      }
      return this.book.awards.slice(0, this.awardsLimit);
    },
    shouldShowAwardsToggle() {
      return this.book && this.book.awards && this.book.awards.length > this.awardsLimit;
    }
  },
  //埋点
  mounted() {
    this.pageViewStartTime = Date.now();
    this.pageUrlOnMount = window.location.href;
  },
  beforeUnmount() {
    const endTime = Date.now();
    const dwellTimeInSeconds = Math.round((endTime - this.pageViewStartTime) / 1000);
    trackPageView('BookDetails', dwellTimeInSeconds, this.pageUrlOnMount);
  },
  // 监听路由参数变化，当 bookId 变化时重新加载数据
  watch: {
    '$route.params.bookId': {
      handler(newBookId, oldBookId) {
        // 只有当 bookId 实际发生变化时才重新加载，避免不必要的调用
        if (newBookId !== oldBookId) {
          this.loadBookData();
        }
      },
      immediate: true // 立即执行一次，确保组件初始化时加载数据
    }
  },
  methods: {
    /**
    * 切换评论输入框的显示/隐藏状态
    * @param {string} reviewId - 要切换评论的 reviewId
    */
    toggleCommentInput(reviewId) {
      this.showCommentInput = this.showCommentInput === reviewId ? null : reviewId;
      if (this.showCommentInput === reviewId && (!this.commentsByReview[reviewId] || this.commentsByReview[reviewId].length === 0)) {
        // 如果显示评论输入框且尚未加载评论，则加载评论
        this.loadCommentsForReview(reviewId);
      }
    },

    /**
     * 加载指定书评的评论
     * @param {string} reviewId - 书评ID
     * @param {number} page - 要加载的页码
     */
    async loadCommentsForReview(reviewId, page = 1) {
      try {
        // 初始化评论列表和页码
        if (!this.commentsByReview[reviewId]) {
          this.commentsByReview[reviewId] = []; // 直接赋值即可
        }
        if (!this.commentsPage[reviewId]) {
          this.commentsPage[reviewId] = 1;
        }

        const response = await fetch(`/service-c/api/reviews/${reviewId}/comments?page=${page}&per_page=${this.commentsPerPage}`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || `Failed to fetch comments for review ${reviewId}`);
        }
        const result = await response.json();

        // 关键修改：更稳健地检查 result.comments
        // 确保 result 存在，result.comments 存在，并且 result.comments 是一个数组
        if (!result || !result.comments || !Array.isArray(result.comments)) {
          console.warn(`API response for review ${reviewId} comments is invalid or missing 'comments' array. Full response:`, result);
          // 如果数据结构不符合预期，将其设置为一个空数组以防止后续错误
          this.commentsByReview[reviewId] = [];
          return; // 提前返回，避免对一个不存在的数组进行 map 操作
        }

        // 现在可以安全地对 result.comments 进行 map 操作
        const commentsWithUserDetails = await Promise.all(result.comments.map(async comment => {
          // ... 你的现有逻辑，用于获取评论者的昵称和头像，并处理时间 ...
          let commenterNickname = '匿名用户';
          let commenterAvatarUrl = 'https://via.placeholder.com/50/CCCCCC/FFFFFF?text=AV';
          try {
            const userProfile = await axios.get(`/service-a/api/users/${comment.userId}`);
            commenterNickname = userProfile.data.nickname || '匿名用户';
            commenterAvatarUrl = userProfile.data.avatar_url || 'https://via.placeholder.com/50/CCCCCC/FFFFFF?text=AV';
          } catch (userError) {
            console.warn(`Could not fetch user info for comment userId ${comment.userId}:`, userError);
          }

          let parsedDate = null;
          if (typeof comment.commentTime === 'string') { // 将 postTime 改为 commentTime
            parsedDate = new Date(comment.commentTime);
            if (isNaN(parsedDate.getTime())) {
              console.error('Date parsing failed for commentTime:', comment.commentTime); // 错误信息也同步修改
              parsedDate = null;
            }
          } else if (comment.commentTime instanceof Date) { // 将 postTime 改为 commentTime
            parsedDate = comment.commentTime;
          }

          return {
            ...comment,
            commenterNickname,
            commenterAvatarUrl,
            commentTime: parsedDate // 将 post_time 改为 commentTime
          };
        }));


        // 如果是加载第一页，则直接赋值；否则追加
        if (page === 1) {
          this.commentsByReview[reviewId] = commentsWithUserDetails;
        } else {
          this.commentsByReview[reviewId] = [...this.commentsByReview[reviewId], ...commentsWithUserDetails];
        }
        this.commentsPage[reviewId] = page; // 更新当前页码
      } catch (error) {
        console.error("Error loading comments:", error);
        alert(`Failed to load comments: ${error.message}`);
      }
    },

    /**
     * 提交新评论
     * @param {string} reviewId - 书评ID
     */
    async submitComment(reviewId) {
      if (!this.newCommentContent.trim()) {
        alert("评论内容不能为空！");
        return;
      }

      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能提交评论！');
        return;
      }

      try {
        const response = await fetch(`/service-c/api/reviews/${reviewId}/comments`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            userId: userId,
            content: this.newCommentContent, // 这里发送了 content
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "提交评论失败");
        }

        const backendResponse = await response.json(); // 后端返回的是 { message, commentId }

        // 获取当前时间作为评论时间，因为后端没有返回
        const currentCommentTime = new Date();

        // 立即获取新评论的作者信息
        let commenterNickname = this.getCurrentUserNickname;
        let commenterAvatarUrl = this.getCurrentUserAvatar;

        // ***关键修改：手动构造完整的评论对象***
        const processedNewComment = {
          // 后端返回的只有 commentId
          id: backendResponse.commentId, // 使用后端返回的 commentId 作为唯一标识
          reviewId: reviewId, // 添加 reviewId
          userId: userId, // 添加 userId
          content: this.newCommentContent, // 从输入框中获取 content
          commentTime: currentCommentTime, // 使用前端获取的当前时间
          likeCount: 0, // 新评论通常默认点赞数为0
          commenterNickname,
          commenterAvatarUrl,
        };

        // 将新评论添加到对应的书评评论列表中
        if (!this.commentsByReview[reviewId]) {
          this.$set(this.commentsByReview, reviewId, []);
        }
        this.commentsByReview[reviewId].unshift(processedNewComment); // 添加到评论列表的开头

        this.newCommentContent = ''; // 清空输入框
        alert("评论发布成功！");
      } catch (error) {
        console.error("提交评论时出错:", error);
        alert(`发布评论失败: ${error.message}`);
      }
    },

    /**
     * 加载更多评论
     * @param {string} reviewId - 书评ID
     */
    loadMoreComments(reviewId) {
      const nextPage = this.commentsPage[reviewId] + 1;
      this.loadCommentsForReview(reviewId, nextPage);
    },

    /**
     * 删除评论
     * @param {string} commentId - 评论ID
     * @param {string} reviewId - 评论所属的书评ID
     */
    async deleteComment(commentId, reviewId) {
      if (!confirm("Are you sure you want to delete this comment?")) {
        return;
      }

      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能删除评论！');
        return;
      }

      try {
        // 确保后端有权限验证：即只有评论作者或管理员才能删除
        const response = await fetch(`/service-c/api/comments/${commentId}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ userId: userId }) // 将 userId 放在 body 中，如果后端需要
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Failed to delete comment");
        }

        // 从本地评论列表中移除已删除的评论
        this.commentsByReview[reviewId] = this.commentsByReview[reviewId].filter(
          (comment) => comment.id !== commentId
        );
        alert("Comment deleted successfully!");
      } catch (error) {
        console.error("Error deleting comment:", error);
        alert(`Failed to delete comment: ${error.message}`);
      }
    },

    // 统一的加载数据方法
    async loadBookData() {
      this.loading = true;
      try {
        await this.fetchBookDetails(); // 获取书籍详情
        if (this.book && this.book.bookId) {
          await Promise.all([
            this.fetchBookReviews(), // 获取书评
            this.fetchUserEngagementStatus(), // 获取用户对书籍的点赞收藏状态
            this.performDoubanSearch(this.book.title), // 执行豆瓣搜索
            this.fetchRealtimeRecommendations() // 获取实时推荐
          ]);
        } else {
          // 如果 book 为空，清空相关数据，防止显示旧数据或残留状态
          this.bookReviews = [];
          this.doubanSearchResults = [];
          this.realtimeRecommendations = [];
          this.isLiked = false;
          this.likeCount = 0;
          this.isCollected = false;
          // 清空评论相关数据
          this.showCommentInput = null;
          this.newCommentContent = '';
          this.commentsByReview = {};
          this.commentsPage = {};
        }
      } catch (error) {
        console.error('Error loading book data:', error);
        this.book = null;
        this.bookReviews = [];
        this.doubanSearchResults = [];
        this.realtimeRecommendations = [];
        this.isLiked = false;
        this.likeCount = 0;
        this.isCollected = false;
        // 清空评论相关数据
        this.showCommentInput = null;
        this.newCommentContent = '';
        this.commentsByReview = {};
        this.commentsPage = {};
      } finally {
        this.loading = false;
      }
    },
    async fetchBookDetails() {
      try {
        const bookId = this.$route.params.bookId;
        const response = await axios.get(`/service-b/api/books/${bookId}`);
        this.book = response.data;
      } catch (error) {
        console.error('Error fetching book details:', error);
        this.book = null;
      }
    },

    readOnline() {
      if (!this.book || !this.book.epubUrl) {
        console.error("EPUB URL is not available for reading online.");
        alert("该书籍暂无在线阅读资源。");
        return;
      }

      this.$router.push({
        name: 'EpubReader',
        params: {
          bookId: this.book.bookId,
          epubUrl: encodeURIComponent(this.book.epubUrl)
        }
      });
    },

    async fetchUserEngagementStatus() {
      const userId = this.currentUserId;
      const bookId = this.book.bookId;

      try {
        const likeCountResponse = await axios.get(`/service-c/api/books/${bookId}/total_likes`);
        this.likeCount = likeCountResponse.data.totalLikeCount;
      } catch (error) {
        console.error('Error fetching total like count:', error);
        this.likeCount = 0;
      }

      if (!userId) {
        console.log("User not logged in. Displaying total counts only.");
        this.isLiked = false;
        this.isCollected = false;
        return;
      }

      try {
        const likeStatusResponse = await axios.get(`/service-c/api/books/${bookId}/like_status`, {
          params: { userId }
        });
        this.isLiked = likeStatusResponse.data.isLiked;
      } catch (error) {
        console.error('Error fetching user like status:', error);
        this.isLiked = false;
      }

      try {
        const collectStatusResponse = await axios.get(`/service-c/api/books/${bookId}/favorite_status`, {
          params: { userId }
        });
        this.isCollected = collectStatusResponse.data.isFavorited;
      } catch (error) {
        console.error('Error fetching user collect status:', error);
        this.isCollected = false;
      }
    },
    async toggleLike() {
      trackButtonClick('LikeButton', 'BookDetails', { bookId: this.book?.bookId });

      if (!this.book || !this.book.bookId) return;

      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能点赞！');
        return;
      }
      const endpoint = `/service-c/api/books/${this.book.bookId}/like`;

      try {
        const response = await axios.post(endpoint, { userId });
        this.isLiked = response.data.isLiked;
        this.likeCount = response.data.likeCount;
        console.log(`Book ${this.isLiked ? 'liked' : 'unliked'}! Current likes: ${this.likeCount}`);
        this.fetchRealtimeRecommendations();
      } catch (error) {
        console.error('Error toggling book like status:', error);
        alert('Failed to update book like status. Please try again.');
      }
    },
    async toggleCollect() {
      trackButtonClick('CollectButton', 'BookDetails', { bookId: this.book?.bookId });
      if (!this.book || !this.book.bookId) return;

      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能收藏！');
        return;
      }
      const endpoint = `/service-c/api/books/${this.book.bookId}/favorite`;

      try {
        const response = await axios.post(endpoint, { userId });
        this.isCollected = response.data.isFavorited;
        console.log(`Book ${this.isCollected ? 'collected' : 'uncollected'}!`);
        this.fetchRealtimeRecommendations();
      } catch (error) {
        console.error('Error toggling book collect status:', error);
        alert('Failed to update book collection status. Please try again.');
      }
    },
    async fetchBookReviews() {
      if (!this.book || !this.book.bookId) {
        console.warn('Book data or bookId is missing. Cannot fetch reviews.');
        return;
      }
      const bookId = this.book.bookId;
      const userId = this.currentUserId;

      try {
        // 这是获取某本书的所有书评的正确接口
        const reviewsResponse = await axios.get(`/service-c/api/books/${bookId}/reviews`);

        this.bookReviews = await Promise.all(reviewsResponse.data.map(async review => {
          let isLikedByCurrentUser = false;
          let likeCount = review.likeCount || 0;
          let isCollectedByCurrentUser = false; // 书评是否可收藏？如果不能，可以移除
          let collectCount = review.collectCount || 0; // 书评是否可收藏？如果不能，可以移除

          let reviewerNickname = '匿名用户';
          let reviewerAvatarUrl = 'https://via.placeholder.com/50/CCCCCC/FFFFFF?text=AV'; // 统一默认头像

          // 获取书评作者的昵称和头像
          try {
            const userProfile = await axios.get(`/service-a/api/users/${review.userId}`);
            reviewerNickname = userProfile.data.nickname || '匿名用户';
            reviewerAvatarUrl = userProfile.data.avatar_url || 'https://via.placeholder.com/50/CCCCCC/FFFFFF?text=AV';
          } catch (userError) {
            console.warn(`Could not fetch user info for review userId ${review.userId}:`, userError);
          }

          if (userId) {
            try {
              const reviewLikeStatus = await axios.get(`/service-c/api/reviews/${review.id}/like_status`, {
                params: { userId }
              });
              isLikedByCurrentUser = reviewLikeStatus.data.isLiked;
              likeCount = reviewLikeStatus.data.likeCount;
            } catch (likeError) {
              console.warn(`Could not fetch like status for review ${review.id}:`, likeError);
            }

            // 如果书评有收藏功能，保留此段
            try {
              const reviewFavoriteStatus = await axios.get(`/service-c/api/reviews/${review.id}/favorite_status`, {
                params: { userId }
              });
              isCollectedByCurrentUser = reviewFavoriteStatus.data.isFavorited;
              collectCount = reviewFavoriteStatus.data.favoriteCount;
            } catch (favError) {
              console.warn(`Could not fetch favorite status for review ${review.id}:`, favError);
            }
          }

          let parsedDate = null;
          if (typeof review.postTime === 'string') {
            parsedDate = new Date(review.postTime);
            if (isNaN(parsedDate.getTime())) {
              console.error('Date parsing failed for postTime:', review.postTime);
              parsedDate = null;
            }
          } else if (review.postTime instanceof Date) {
            parsedDate = review.postTime;
          }

          return {
            ...review,
            reviewerNickname,
            reviewerAvatarUrl,
            likeCount,
            isLikedByCurrentUser,
            collectCount,
            isCollectedByCurrentUser,
            post_time: parsedDate,
            // 确保 rating 字段存在，如果后端不提供，默认为0
            rating: review.rating || 0
          };
        }));
        console.log('Fetched reviews with parsed dates:', this.bookReviews);
      } catch (error) {
        console.error('Error fetching book reviews:', error);
        this.bookReviews = [];
      }
    },
    async submitReview() {
      trackButtonClick('SubmitReview', 'BookDetails', { bookId: this.book?.bookId });
      if (!this.book || !this.book.bookId) {
        alert('书籍信息缺失，无法提交评论。');
        return;
      }
      const bookId = this.book.bookId;

      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能提交评论！');
        return;
      }

      if (!this.newReviewContent.trim() || this.newReviewRating === 0) {
        alert('请输入评论内容并选择评分。');
        return;
      }

      try {
        // 这是为书本提交新书评的正确接口
        const response = await axios.post(`/service-c/api/books/${bookId}/reviews`, {
          userId: userId,
          content: this.newReviewContent,
          rating: this.newReviewRating,
        });
        console.log('Review submitted:', response.data);
        alert('评论提交成功！');
        this.newReviewContent = '';
        this.newReviewRating = 0;
        await this.fetchBookReviews(); // 重新加载书评列表以显示新提交的书评
        this.fetchRealtimeRecommendations(); // 刷新实时推荐
      } catch (error) {
        console.error('Error submitting review:', error);
        alert('提交评论失败，请重试。');
      }
    },
    async deleteReview(reviewId) {
      const userId = this.currentUserId;

      if (!userId) {
        alert('请先登录才能删除评论！');
        return;
      }

      if (!confirm('确定要删除这条评论吗？')) {
        return;
      }

      try {
        // 确保后端有权限验证：即只有书评作者或管理员才能删除
        const response = await axios.delete(`/service-c/api/reviews/${reviewId}`, {
          params: { userId: userId } // 将 userId 作为查询参数传递，后端用于验证
        });
        console.log('Review deleted:', response.data);
        alert('评论删除成功！');
        await this.fetchBookReviews(); // 重新加载书评列表
        this.fetchRealtimeRecommendations(); // 刷新实时推荐
      } catch (error) {
        console.error('Error deleting review:', error);
        alert('删除评论失败，请重试。');
      }
    },
    async toggleReviewLike(review) {
      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能点赞评论！');
        return;
      }
      const endpoint = `/service-c/api/reviews/${review.id}/like`;

      try {
        const response = await axios.post(endpoint, { userId });
        review.isLikedByCurrentUser = response.data.isLiked;
        review.likeCount = response.data.likeCount;
        this.fetchRealtimeRecommendations();
      } catch (error) {
        console.error('Error toggling review like status:', error);
        alert('更新评论点赞状态失败，请重试。');
      }
    },
    async toggleReviewCollect(review) {
      const userId = this.currentUserId;
      if (!userId) {
        alert('请先登录才能收藏评论！');
        return;
      }
      const endpoint = `/service-c/api/reviews/${review.id}/favorite`;

      try {
        const response = await axios.post(endpoint, { userId });
        review.isCollectedByCurrentUser = response.data.isFavorited;
        review.collectCount = response.data.favoriteCount;
        this.fetchRealtimeRecommendations();
      } catch (error) {
        console.error('Error toggling review collect status:', error);
        alert('更新评论收藏状态失败，请重试。');
      }
    },
    goBack() {
      this.$router.go(-1);
    },
    async performDoubanSearch(keyword) {
      if (!keyword.trim()) {
        console.warn('Douban search keyword is empty, skipping search.');
        return;
      }
      this.searched = true;
      this.doubanSearchResults = [];
      try {
        const response = await axios.get(
          `/service-b/api/search_douban?keyword=${encodeURIComponent(keyword)}`
        );
        this.doubanSearchResults = response.data;
      } catch (error) {
        console.error('Error fetching Douban books:', error);
      }
    },
    toggleDoubanResults() {
      this.showDoubanResults = !this.showDoubanResults;
    },
    toggleDescription() {
      this.showFullDescription = !this.showFullDescription;
    },
    toggleAwards() {
      this.showAllAwards = !this.showAllAwards;
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return dateString;
      }
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
    },
    async fetchRealtimeRecommendations() {
      const userId = this.currentUserId;
      if (!userId) {
        console.log("用户未登录，无法获取实时推荐。");
        this.realtimeRecommendations = [];
        return;
      }

      this.loadingRecommendations = true;
      try {
        const response = await axios.get(`/service-f/realtime_updated_recommendations/${userId}`);
        this.realtimeRecommendations = response.data.recommendations || [];
        console.log("实时推荐数据:", this.realtimeRecommendations);

      } catch (error) {
        console.error('Error fetching realtime recommendations:', error);
        this.realtimeRecommendations = [];
      } finally {
        this.loadingRecommendations = false;
      }
    },
  },
};
</script>

<style scoped>
/* A Font of Ages: Evoking the Scribe's Hand */
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Playfair+Display:wght@400;700&display=swap');

/* 评论区样式 */
.comments-section {
  margin-top: 15px;
  border-top: 1px solid #eee;
  padding-top: 15px;
  background-color: #fcfcfc;
  border-radius: 8px;
  padding: 15px;
}

.comment-submission-form {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.comment-textarea {
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  margin-bottom: 10px;
  font-family: inherit;
  font-size: 0.9em;
}

.submit-comment-button {
  align-self: flex-end;
  background-color: #4CAF50;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 0;
  /* 确保不被前面的 margin-right 影响 */
}

.submit-comment-button:hover {
  background-color: #45a049;
}

.existing-comments-list {
  margin-top: 15px;
}

.no-comments-message {
  font-style: italic;
  color: #777;
  text-align: center;
  padding: 10px 0;
}

.comment-entry {
  border: 1px solid #eee;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
  background-color: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
  font-size: 0.9em;
  color: #555;
  flex-wrap: wrap;
  /* 允许换行 */
}

.commenter-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-right: 8px;
  object-fit: cover;
}

.commenter-name {
  font-weight: bold;
  margin-right: 10px;
  color: #333;
}

.comment-date {
  color: #999;
  font-size: 0.8em;
  margin-left: auto;
  /* 将日期推到右边 */
}

.comment-content {
  margin-left: 38px;
  /* 与头像对齐 */
  line-height: 1.5;
  color: #444;
}

.delete-comment-button,
.delete-review-button {
  background-color: #dc3545;
  /* Red */
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.8em;
  margin-left: 10px;
  /* 与日期等元素保持距离 */
}

.delete-comment-button:hover,
.delete-review-button:hover {
  background-color: #c82333;
}

.load-more-comments-button {
  display: block;
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
  font-size: 14px;
  text-align: center;
}

.load-more-comments-button:hover {
  background-color: #0056b3;
}

/* Add some basic styling for the new buttons */
.tome-interactive-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: flex-start;
  align-items: center;
}

.action-button {
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.2s, border-color 0.2s;
}

.action-button:hover {
  background-color: #e0e0e0;
}

.action-button.liked {
  background-color: #ffebee;
  /* Light red for liked */
  border-color: #ef9a9a;
  color: #d32f2f;
  /* Darker red */
}

.action-button.collected {
  background-color: #e8f5e9;
  /* Light green for collected */
  border-color: #a5d6a7;
  color: #388e3c;
  /* Darker green */
}

.action-button .icon {
  font-size: 1.2em;
  line-height: 1;
}


/* The Ancient Scroll Layout */
.ancient-scroll-page {
  display: flex;
  max-width: 1300px;
  margin: 3rem auto;
  gap: 2.5rem;
  align-items: flex-start;
  padding: 0 1.5rem;
  font-family: 'Merriweather', serif;
  color: #3b2f2f;
  /* Deep Ink */
  position: relative;
}

/* Base Parchment Style */
.main-parchment-folio,
.scribe-notes-sidebar {
  background: #fdfaf3;
  /* Old Paper */
  border: 1px solid #d4c7b2;
  border-radius: 8px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  position: relative;
}

.main-parchment-folio {
  flex: 3;
  min-width: 65%;
}

.scribe-notes-sidebar {
  flex: 1;
  min-width: 320px;
  position: sticky;
  top: 3rem;
  height: fit-content;
}

/* Tome Unveiling Header */
.tome-unveiling-header {
  display: flex;
  gap: 2.5rem;
  margin-bottom: 2.5rem;
  align-items: flex-start;
}

.tome-illumination {
  flex-shrink: 0;
  width: 220px;
  height: 320px;
  overflow: hidden;
  background-color: #e8e0d4;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #d4c7b2;
  position: relative;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.tome-illumination::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to right, rgba(253, 250, 243, 0) 0%, rgba(253, 250, 243, 0.3) 100%);
  pointer-events: none;
}

.tome-cover-illustration {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
  transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.tome-cover-illustration:hover {
  transform: scale(1.05) rotateZ(1deg);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.tome-essential-data {
  flex-grow: 1;
}

.tome-grand-title {
  font-family: 'Playfair Display', serif;
  font-size: 2.8em;
  color: #5a4b41;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

.tome-series-chapter {
  font-family: 'Merriweather', serif;
  font-size: 1.2em;
  color: #7b6a5e;
  margin-top: 0;
  margin-bottom: 1rem;
  font-style: italic;
}

.tome-scribe {
  font-size: 1.1em;
  color: #5a4b41;
  margin-bottom: 1.5rem;
}

.celestial-judgement {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
}

.stars-bestowed {
  color: #e6b800;
  /* Gold */
  font-size: 1.8em;
  margin-right: 0.6rem;
  letter-spacing: 0.05em;
}

.whispers-of-appraisal {
  font-size: 0.95em;
  color: #8c7f73;
}

/* Optimized Provenance Details Grid */
.tome-provenance-details-grid {
  margin-top: 1.5rem;
  font-size: 0.95em;
  color: #7b6a5e;
  display: grid;
  /* Use CSS Grid for flexible columns */
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  /* Adjust minmax as needed */
  gap: 0.8rem 1.5rem;
  /* Row and column gap */
  padding-top: 1.5rem;
  border-top: 1px dashed #e0d4c0;
}

.detail-item {
  display: flex;
  /* Ensures strong and text stay on one line if possible */
  flex-wrap: wrap;
  /* Allows wrapping if content is too long */
  align-items: baseline;
  /* Aligns first line of text */
}

.detail-item strong {
  font-weight: 700;
  margin-right: 0.3em;
  /* Small space after label */
  flex-shrink: 0;
  /* Prevents label from shrinking */
}


.scholarly-genres-seals {
  margin-top: 1.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.genre-crest,
.character-sigil,
.setting-marker {
  display: inline-block;
  background-color: #e0d4c0;
  color: #5a4b41;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  /* margin-right removed as gap handles spacing */
  /* margin-bottom removed as gap handles spacing */
  font-size: 0.85em;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: 1px solid #d4c7b2;
}

.genre-crest:hover,
.character-sigil:hover,
.setting-marker:hover {
  background-color: #d4c7b2;
  transform: translateY(-2px) rotateZ(-1deg);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.tome-narrative-summary {
  margin-top: 2.5rem;
}

.section-heading {
  font-family: 'Playfair Display', serif;
  font-size: 1.8em;
  color: #5a4b41;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e0d4c0;
}

.summary-parchment {
  line-height: 1.8;
  color: #4b3e3e;
  text-align: justify;
}

.tome-additional-annotations {
  margin-top: 2.5rem;
  padding-top: 2rem;
  border-top: 1px dashed #d4c7b2;
}

.characters-of-note,
.settings-of-the-tale {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 1.5rem;
}

.laurels-list {
  list-style-type: disc;
  margin-left: 1.5rem;
  padding: 0;
  color: #5a4b41;
}

.laurels-list li {
  margin-bottom: 0.5rem;
}

/* Grouping Affection & Distribution for better layout */
.readership-stats-group {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px dashed #d4c7b2;
}

.stats-content-flex {
  display: flex;
  flex-wrap: wrap;
  /* Allow wrapping on smaller screens */
  gap: 2rem;
  /* Space between the two sections */
  align-items: flex-start;
}

.affection-measure-container {
  flex: 1;
  min-width: 250px;
  /* Ensure it doesn't get too narrow */
}

.affection-measure {
  font-size: 1em;
  color: #5a4b41;
  font-style: italic;
  margin-bottom: 1.5rem;
  /* Space before next section if stacked */
}

.critique-distribution {
  flex: 1.5;
  /* Give more space to bars */
  min-width: 300px;
  /* Ensure it doesn't get too narrow */
  margin-top: 0;
  /* Reset margin if inherited */
}

.star-critique-row {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.95em;
  color: #7b6a5e;
}

.star-critique-row span:first-child {
  width: 70px;
  flex-shrink: 0;
  font-weight: 600;
}

.star-bar-scroll-container {
  flex-grow: 1;
  background-color: #eee;
  height: 10px;
  border-radius: 5px;
  margin: 0 0.8rem;
  overflow: hidden;
  border: 1px solid #d4c7b2;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
}

.star-bar-illumination {
  height: 100%;
  background-color: #e6b800;
  /* Gold */
  border-radius: 5px;
  transition: width 0.5s ease-out;
}

/* Actions Section */
.tome-actions {
  margin-top: 2.5rem;
  text-align: center;
  border-top: 1px dashed #e0d4c0;
  padding-top: 2rem;
}

.return-to-catalogue-button {
  padding: 0.8rem 1.8rem;
  background-color: #8d6e63;
  /* Deep Sepia */
  color: #fdfaf3;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1em;
  transition: all 0.3s ease-in-out;
  font-family: 'Playfair Display', serif;
  letter-spacing: 0.05em;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.return-to-catalogue-button:hover {
  background-color: #6d5448;
  transform: translateY(-3px) scale(1.01);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25);
}

.return-to-catalogue-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* Scribe Notes Sidebar */
.sidebar-section-header {
  cursor: pointer;
  padding: 1rem;
  background-color: #f0ebe0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
  transition: background-color 0.2s ease, transform 0.2s ease;
  border: 1px solid #d4c7b2;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.sidebar-section-header:hover {
  background-color: #e5e0d4;
  transform: translateY(-2px);
}

.sidebar-section-title {
  margin: 0;
  font-family: 'Playfair Display', serif;
  font-size: 1.5em;
  color: #5a4b41;
  display: flex;
  align-items: center;
  flex-grow: 1;
}

.toggle-rune {
  margin-left: 1rem;
  font-size: 0.7em;
  color: #8c7f73;
  transition: transform 0.3s ease;
}

.sidebar-section-header:hover .toggle-rune {
  transform: rotate(5deg);
}

.oracle-douban-section {
  margin-bottom: 2rem;
}

.oracle-results-container {
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e0d4c0;
  box-shadow: inset 0 1px 5px rgba(0, 0, 0, 0.05);
  padding: 1.2rem 1.5rem;
}

.oracle-findings-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.oracle-finding-item {
  padding: 0.8rem 0;
  border-bottom: 1px dashed #e0d4c0;
  transition: background-color 0.2s ease;
}

.oracle-finding-item:last-child {
  border-bottom: none;
}

.oracle-finding-item:hover {
  background-color: #f9f7f0;
}

.oracle-link {
  color: #8d6e63;
  /* Deep Sepia */
  text-decoration: none;
  display: block;
  margin-bottom: 0.3rem;
  font-weight: 600;
  transition: color 0.2s ease;
}

.oracle-link:hover {
  text-decoration: underline;
  color: #6d5448;
}

.douban-oracle-rating {
  color: #e6b800;
  font-size: 0.9em;
  display: block;
}

.no-oracle-findings {
  color: #7b6a5e;
  font-style: italic;
  padding: 1rem 0;
  text-align: center;
}

.scribe-notes-section {
  padding: 1.5rem;
}

.scribe-notes-section .sidebar-section-title {
  border-bottom: 1px dashed #e0d4c0;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.sidebar-text {
  color: #5a4b41;
  font-size: 0.95em;
  line-height: 1.6;
}

/* Transition for Douban Results (Unfurl Scroll Effect) */
.unfurl-scroll-enter-active,
.unfurl-scroll-leave-active {
  transition: all 0.4s ease-out;
  max-height: 500px;
  overflow: hidden;
}

.unfurl-scroll-enter-from,
.unfurl-scroll-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-20px);
}


/* Loading and Not Found States */
.scribe-at-work,
.tome-vanished {
  text-align: center;
  padding: 5rem;
  font-size: 1.5em;
  color: #7b6a5e;
  width: 100%;
  font-family: 'Playfair Display', serif;
  font-style: italic;
}

/* Responsive Adaptations for Smaller Screens (Papyrus Roll Adjustment) */
@media (max-width: 992px) {
  .ancient-scroll-page {
    flex-direction: column;
    align-items: center;
  }

  .main-parchment-folio,
  .scribe-notes-sidebar {
    min-width: auto;
    width: 100%;
    padding: 2rem;
  }

  .scribe-notes-sidebar {
    position: static;
    margin-top: 2.5rem;
  }

  .tome-unveiling-header {
    flex-direction: column;
    align-items: center;
  }

  .tome-illumination {
    width: 250px;
    height: 350px;
    border-right: none;
    border-bottom: 1px solid #d4c7b2;
    border-radius: 8px 8px 0 0;
  }

  .tome-illumination::before {
    background: linear-gradient(to bottom, rgba(253, 250, 243, 0) 0%, rgba(253, 250, 243, 0.3) 100%);
  }

  .tome-essential-data {
    text-align: center;
  }

  .tome-grand-title {
    font-size: 2.5em;
  }

  /* Adjust provenance details for smaller screens */
  .tome-provenance-details-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    justify-items: center;
    /* Center items in the grid */
    text-align: center;
  }

  .celestial-judgement,
  .scholarly-genres-seals,
  .characters-of-note,
  .settings-of-the-tale,
  .stats-content-flex {
    justify-content: center;
  }

  .stats-content-flex {
    flex-direction: column;
    /* Stack on smaller screens */
    align-items: center;
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .ancient-scroll-page {
    padding: 0 1rem;
  }

  .main-parchment-folio,
  .scribe-notes-sidebar {
    padding: 1.5rem;
  }

  .tome-grand-title {
    font-size: 2.2em;
  }

  .section-heading {
    font-size: 1.6em;
  }

  .tome-scribe,
  .tome-series-chapter,
  .summary-parchment,
  .tome-provenance-details-grid .detail-item {
    font-size: 0.95em;
  }

  .return-to-catalogue-button {
    font-size: 1em;
    padding: 0.7rem 1.5rem;
  }

  .sidebar-section-title {
    font-size: 1.3em;
  }

  .tome-provenance-details-grid {
    grid-template-columns: 1fr;
    /* Stack on very small screens */
    gap: 0.5rem;
    text-align: left;
    /* Align text left when stacked */
  }

  .detail-item {
    justify-content: center;
    /* Center content when stacked on small screens */
  }
}

@media (max-width: 480px) {
  .tome-illumination {
    width: 180px;
    height: 260px;
  }

  .tome-grand-title {
    font-size: 1.8em;
  }

  .section-heading {
    font-size: 1.4em;
  }

  .genre-crest,
  .character-sigil,
  .setting-marker {
    font-size: 0.8em;
    padding: 0.4rem 0.8rem;
  }
}

/* New styles for the Book Reviews Section */
/* New styles for "Show More" buttons */
.toggle-text-button {
  color: #7a5f4c;
  /* A darker earthy tone for the link */
  cursor: pointer;
  margin-left: 5px;
  font-weight: bold;
  text-decoration: underline;
  transition: color 0.3s ease;
}

.toggle-text-button:hover {
  color: #5a3c2f;
  /* Darker on hover */
}

.toggle-list-item {
  list-style: none;
  /* Remove bullet point for this specific list item */
  text-align: right;
  /* Align the "Show More" link to the right */
  margin-top: 10px;
}

/* Existing styles for the Book Reviews Section */
.tome-reviews-section {
  background-color: #fdfaf2;
  border: 1px solid #d4c29a;
  border-radius: 8px;
  padding: 20px;
  margin-top: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.tome-reviews-section .section-heading {
  color: #5a3c2f;
  font-family: 'Georgia', serif;
  font-size: 1.8em;
  margin-bottom: 20px;
  text-align: center;
  position: relative;
}

.tome-reviews-section .section-heading::after {
  content: '';
  display: block;
  width: 50px;
  height: 2px;
  background: #d4c29a;
  margin: 10px auto 0;
}

.review-submission-form {
  background-color: #fffbf5;
  border: 1px dashed #d4c29a;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 25px;
}

.review-submission-form h4 {
  color: #5a3c2f;
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.2em;
}

.review-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #d4c29a;
  border-radius: 4px;
  font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
  font-size: 1em;
  color: #333;
  resize: vertical;
  margin-bottom: 10px;
  background-color: #fefdfb;
}

.review-rating-input {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.review-rating-input label {
  color: #5a3c2f;
  font-weight: bold;
}

.review-rating-select {
  padding: 8px;
  border: 1px solid #d4c29a;
  border-radius: 4px;
  background-color: #fefdfb;
  font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
}

.submit-review-button {
  background-color: #a08462;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  font-family: 'Georgia', serif;
  transition: background-color 0.3s ease;
}

.submit-review-button:hover {
  background-color: #8c735a;
}

.existing-reviews-list {
  margin-top: 20px;
}

.no-reviews-message {
  text-align: center;
  color: #777;
  font-style: italic;
  padding: 20px;
  border: 1px dashed #e0d0b0;
  border-radius: 5px;
  background-color: #fffaf0;
}

.review-entry {
  background-color: #fffef9;
  border: 1px solid #e0d0b0;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.reviewer-name {
  font-weight: bold;
  color: #5a3c2f;
  font-size: 1.1em;
}

.review-date {
  font-size: 0.9em;
  color: #777;
  margin-left: auto;
  padding-left: 10px;
}

.review-stars {
  color: #f39c12;
  font-size: 1.2em;
  margin-left: 10px;
}

.review-content {
  color: #333;
  line-height: 1.6;
  margin-bottom: 15px;
}

.review-actions {
  display: flex;
  gap: 15px;
}

.review-action-button {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 12px;
  border: 1px solid #d4c29a;
  border-radius: 4px;
  background-color: #fcf8f0;
  color: #5a3c2f;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.review-action-button:hover {
  background-color: #f0e6da;
  border-color: #a08462;
}

.review-action-button .icon {
  font-size: 1.1em;
}

.review-action-button.liked {
  background-color: #ffebee;
  border-color: #e74c3c;
  color: #e74c3c;
}

.review-action-button.collected {
  background-color: #e8f5e9;
  border-color: #27ae60;
  color: #27ae60;
}

/* 这里可以添加针对实时推荐区域的样式 */
.realtime-recommendations-section {
  background-color: #fcf8e3;
  border: 1px solid #d4c8a2;
  border-radius: 8px;
  padding: 15px;
  margin-top: 20px;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
}

.realtime-recommendations-section .sidebar-section-title {
  color: #8b4513;
  font-family: 'Georgia', serif;
  font-size: 1.3em;
  margin-bottom: 15px;
  text-align: center;
  border-bottom: 1px dashed #d4c8a2;
  padding-bottom: 10px;
}

.recommendations-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.recommendation-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px;
  border-bottom: 1px dashed #e0d8c2;
  transition: background-color 0.3s ease;
}

.recommendation-item:last-child {
  border-bottom: none;
}

.recommendation-item:hover {
  background-color: #f5f0d9;
}

.recommendation-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: inherit;
  width: 100%;
}

.recommendation-cover {
  width: 50px;
  height: 75px;
  object-fit: cover;
  margin-right: 10px;
  border: 1px solid #d4c8a2;
  box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.05);
}

.recommendation-info {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.recommendation-title {
  font-weight: bold;
  color: #5a3d2b;
  font-size: 1em;
  line-height: 1.3;
}

.recommendation-author {
  font-size: 0.85em;
  color: #7b6d5f;
  margin-top: 3px;
}

.no-recommendations-message,
.loading-message {
  text-align: center;
  color: #7b6d5f;
  font-style: italic;
  padding: 10px;
}

.reviewer-avatar {
  width: 30px;
  /* Adjust size as needed */
  height: 30px;
  border-radius: 50%;
  /* Make it round */
  margin-right: 10px;
  /* Space from name */
  object-fit: cover;
  /* Ensure image covers the area */
}
</style>