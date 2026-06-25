<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart.js'
import { useAuthStore } from '../stores/auth.js'
import api from '../api/index.js'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()

const product = ref(null)
const loading = ref(true)
const reviewForm = ref({ rating: 5, comment_text: '' })
const reviewError = ref('')
const reviewSuccess = ref('')
const submitting = ref(false)

onMounted(async () => {
  try {
    const { data } = await api.get(`/products/${route.params.id}`)
    product.value = data
  } finally {
    loading.value = false
  }
})

async function submitReview() {
  reviewError.value = ''
  reviewSuccess.value = ''
  submitting.value = true
  try {
    await api.post('/reviews', {
      product_id: product.value.id,
      rating: reviewForm.value.rating,
      comment_text: reviewForm.value.comment_text || undefined,
    })
    reviewSuccess.value = 'Отзыв успешно добавлен'
    const { data } = await api.get(`/products/${route.params.id}`)
    product.value = data
  } catch (e) {
    reviewError.value = e.response?.data?.detail || 'Ошибка при отправке отзыва'
  } finally {
    submitting.value = false
  }
}

function stars(r) {
  const n = Math.round(r)
  return '★'.repeat(n) + '☆'.repeat(5 - n)
}

function handleCart() {
  if (!auth.isAuthenticated) { router.push('/login'); return }
  if (!auth.isCustomer) return
  cart.add(product.value)
}
</script>

<template>
  <div v-if="loading" class="empty-state">Загрузка...</div>

  <div v-else-if="product">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <router-link to="/catalog">Каталог</router-link>
      <span class="sep">›</span>
      <span>{{ product.type_name }}</span>
      <span class="sep">›</span>
      <span class="current">{{ product.name }}</span>
    </div>

    <!-- Product hero -->
    <div class="card product-hero">
      <div class="hero-left">
        <div class="hero-img">
          <span class="img-placeholder">{{ product.name.slice(0,2).toUpperCase() }}</span>
        </div>
      </div>
      <div class="hero-right">
        <div class="hero-meta">
          <span class="badge badge-gray">{{ product.type_name }}</span>
          <span class="seller-link muted text-sm">{{ product.seller_name }}</span>
        </div>

        <h1 class="hero-title">{{ product.name }}</h1>

        <div class="hero-rating" v-if="product.avg_rating">
          <span class="stars-lg">{{ stars(product.avg_rating) }}</span>
          <span class="rating-num">{{ product.avg_rating }}</span>
          <span class="muted text-sm">{{ product.review_count }} отзывов</span>
        </div>
        <div v-else class="muted text-sm" style="margin-top:6px">Отзывов пока нет</div>

        <div class="hero-price">{{ product.price.toFixed(2) }} ₽</div>

        <div class="stock-row">
          <span v-if="product.stock_quantity > 0" class="text-success text-sm">
            В наличии: {{ product.stock_quantity }} шт.
          </span>
          <span v-else class="text-danger text-sm">Нет в наличии</span>
        </div>

        <button
          v-if="auth.isCustomer || !auth.isAuthenticated"
          class="btn btn-primary cart-btn"
          @click="handleCart"
          :disabled="product.stock_quantity === 0">
          Добавить в корзину
        </button>
      </div>
    </div>

    <!-- Reviews -->
    <div class="card reviews-card">
      <h2 style="margin-bottom:20px">Отзывы ({{ product.reviews.length }})</h2>

      <!-- Leave review form -->
      <div v-if="auth.isCustomer" class="review-form-wrap">
        <h3 style="margin-bottom:14px">Оставить отзыв</h3>
        <form @submit.prevent="submitReview">
          <div class="rating-pick">
            <label style="margin:0">Оценка</label>
            <div class="stars-pick">
              <button
                v-for="n in [1,2,3,4,5]"
                :key="n"
                type="button"
                class="star-btn"
                :class="{ active: reviewForm.rating >= n }"
                @click="reviewForm.rating = n">★</button>
            </div>
          </div>
          <label style="margin-top:12px">Комментарий</label>
          <textarea
            v-model="reviewForm.comment_text"
            rows="3"
            placeholder="Поделитесь впечатлениями о товаре..."></textarea>
          <div v-if="reviewError" class="error">{{ reviewError }}</div>
          <div v-if="reviewSuccess" class="success-msg">{{ reviewSuccess }}</div>
          <button type="submit" class="btn btn-primary btn-sm" style="margin-top:12px" :disabled="submitting">
            {{ submitting ? 'Отправка...' : 'Отправить отзыв' }}
          </button>
        </form>
      </div>

      <!-- Review list -->
      <div v-if="product.reviews.length === 0" class="empty-state" style="padding:32px">
        Отзывов пока нет
      </div>
      <div v-else class="review-list">
        <div v-for="r in product.reviews" :key="r.id" class="review-item">
          <div class="review-head">
            <div class="reviewer-avatar">{{ r.first_name[0] }}{{ r.last_name[0] }}</div>
            <div>
              <div class="reviewer-name">{{ r.first_name }} {{ r.last_name }}</div>
              <div class="review-date muted text-sm">{{ r.created_at }}</div>
            </div>
            <div class="review-stars">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5-r.rating) }}</div>
          </div>
          <p v-if="r.comment_text" class="review-text">{{ r.comment_text }}</p>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="empty-state">Товар не найден</div>
</template>

<style scoped>
/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 18px;
  font-size: 12.5px;
  color: #94a3b8;
}
.breadcrumb a { color: #64748b; }
.breadcrumb a:hover { color: #4f46e5; }
.sep { color: #cbd5e1; }
.current { color: #475569; }

/* Hero */
.product-hero {
  display: flex;
  gap: 28px;
  margin-bottom: 18px;
}
.hero-left { flex-shrink: 0; }
.hero-img {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.img-placeholder {
  font-size: 48px;
  font-weight: 700;
  color: #a5b4fc;
  letter-spacing: -2px;
}
.hero-right { flex: 1; }
.hero-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.hero-title {
  font-size: 22px;
  margin-bottom: 10px;
  line-height: 1.3;
}
.hero-rating {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 14px;
}
.stars-lg { color: #f59e0b; font-size: 18px; letter-spacing: -1px; }
.rating-num { font-size: 16px; font-weight: 700; color: #1e293b; }
.hero-price {
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 8px;
}
.stock-row { margin-bottom: 20px; }
.cart-btn { padding: 11px 24px; font-size: 14px; }

/* Reviews */
.reviews-card { }
.review-form-wrap {
  background: #f8fafc;
  border-radius: 10px;
  padding: 18px;
  margin-bottom: 24px;
  border: 1px solid #e9edf2;
}
.rating-pick {
  display: flex;
  align-items: center;
  gap: 12px;
}
.stars-pick { display: flex; gap: 3px; }
.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 22px;
  color: #e2e8f0;
  line-height: 1;
  padding: 2px;
  transition: color .1s, transform .1s;
}
.star-btn.active { color: #f59e0b; }
.star-btn:hover { transform: scale(1.15); }

.success-msg {
  font-size: 12.5px;
  color: #059669;
  margin-top: 8px;
  padding: 7px 12px;
  background: #ecfdf5;
  border-radius: 6px;
}

.review-list { display: flex; flex-direction: column; gap: 0; }
.review-item {
  padding: 16px 0;
  border-bottom: 1px solid #f1f5f9;
}
.review-item:last-child { border-bottom: none; }
.review-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.reviewer-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #eef2ff;
  color: #4f46e5;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.reviewer-name { font-size: 13.5px; font-weight: 600; color: #1e293b; }
.review-date { }
.review-stars {
  margin-left: auto;
  color: #f59e0b;
  font-size: 13px;
  letter-spacing: -.5px;
}
.review-text {
  font-size: 13.5px;
  color: #475569;
  line-height: 1.55;
  padding-left: 44px;
}

@media (max-width: 680px) {
  .product-hero { flex-direction: column; }
  .hero-img { width: 100%; height: 160px; }
}
</style>
