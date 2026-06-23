<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCartStore } from '../stores/cart.js'
import { useAuthStore } from '../stores/auth.js'
import api from '../api/index.js'

const route = useRoute()
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
    reviewSuccess.value = 'Отзыв добавлен!'
    const { data } = await api.get(`/products/${route.params.id}`)
    product.value = data
  } catch (e) {
    reviewError.value = e.response?.data?.detail || 'Ошибка'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div v-if="loading" style="text-align:center;padding:60px;color:#999">Загрузка...</div>
  <div v-else-if="product">
    <div class="card" style="margin-bottom:20px">
      <div style="font-size:13px;color:#888;margin-bottom:8px">
        <router-link to="/catalog">Каталог</router-link> / {{ product.type_name }}
      </div>
      <h1 style="font-size:24px;margin-bottom:8px">{{ product.name }}</h1>
      <div style="color:#888;margin-bottom:12px">Продавец: {{ product.seller_name }}</div>
      <div style="display:flex;gap:24px;align-items:center;flex-wrap:wrap">
        <div style="font-size:28px;font-weight:bold;color:#2c3e50">{{ product.price.toFixed(2) }} ₽</div>
        <div>
          <span v-if="product.avg_rating" style="color:#f39c12;font-size:18px">★ {{ product.avg_rating }}</span>
          <span style="color:#999;font-size:13px;margin-left:6px" v-if="product.review_count">({{ product.review_count }} отзывов)</span>
        </div>
        <div :style="{ color: product.stock_quantity > 0 ? '#27ae60' : '#e74c3c' }">
          {{ product.stock_quantity > 0 ? `В наличии: ${product.stock_quantity}` : 'Нет в наличии' }}
        </div>
        <button class="btn btn-primary" @click="cart.add(product)" :disabled="product.stock_quantity === 0" v-if="auth.isCustomer">
          Добавить в корзину
        </button>
      </div>
    </div>

    <div class="card">
      <h2 style="margin-bottom:16px">Отзывы</h2>

      <div v-if="auth.isCustomer" style="margin-bottom:24px;padding-bottom:24px;border-bottom:1px solid #eee">
        <h3 style="font-size:15px;margin-bottom:12px">Оставить отзыв</h3>
        <form @submit.prevent="submitReview">
          <label>Оценка</label>
          <select v-model="reviewForm.rating" style="width:100px">
            <option v-for="n in [5,4,3,2,1]" :key="n" :value="n">{{ n }} ★</option>
          </select>
          <label>Комментарий</label>
          <textarea v-model="reviewForm.comment_text" rows="3" placeholder="Напишите отзыв..."></textarea>
          <div class="error" v-if="reviewError">{{ reviewError }}</div>
          <div style="color:#27ae60;font-size:13px;margin-top:6px" v-if="reviewSuccess">{{ reviewSuccess }}</div>
          <button class="btn btn-primary" style="margin-top:12px" :disabled="submitting">Отправить</button>
        </form>
      </div>

      <div v-if="product.reviews.length === 0" style="color:#999;text-align:center;padding:20px">
        Отзывов пока нет
      </div>
      <div v-for="r in product.reviews" :key="r.id" style="padding:12px 0;border-bottom:1px solid #f0f0f0">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
          <strong>{{ r.first_name }} {{ r.last_name }}</strong>
          <span style="color:#f39c12">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5-r.rating) }}</span>
        </div>
        <div style="color:#666;font-size:13px;margin-bottom:4px">{{ r.created_at }}</div>
        <div v-if="r.comment_text">{{ r.comment_text }}</div>
      </div>
    </div>
  </div>
  <div v-else style="text-align:center;padding:60px">Товар не найден</div>
</template>
