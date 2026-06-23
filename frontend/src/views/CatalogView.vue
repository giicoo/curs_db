<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart.js'
import { useAuthStore } from '../stores/auth.js'
import api from '../api/index.js'

const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()

const products = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)

const types = ref([])
const filters = ref({ type_id: '', seller_id: '', min_price: '', max_price: '', search: '' })

onMounted(async () => {
  const { data } = await api.get('/product-types')
  types.value = data
  await load()
})

watch(page, load)

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (filters.value.type_id) params.type_id = filters.value.type_id
    if (filters.value.seller_id) params.seller_id = filters.value.seller_id
    if (filters.value.min_price) params.min_price = filters.value.min_price
    if (filters.value.max_price) params.max_price = filters.value.max_price
    if (filters.value.search) params.search = filters.value.search
    const { data } = await api.get('/catalog', { params })
    products.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function applyFilters() { page.value = 1; load() }
function resetFilters() { filters.value = { type_id: '', seller_id: '', min_price: '', max_price: '', search: '' }; applyFilters() }

function addToCart(p) {
  if (!auth.isCustomer) { router.push('/login'); return }
  cart.add(p)
}

const pages = () => Math.ceil(total.value / pageSize)
</script>

<template>
  <div>
    <h1 style="margin-bottom:20px">Каталог товаров</h1>

    <div class="card" style="margin-bottom:16px;display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end">
      <div>
        <label>Категория</label>
        <select v-model="filters.type_id" style="width:160px">
          <option value="">Все категории</option>
          <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
      </div>
      <div>
        <label>Цена от</label>
        <input v-model="filters.min_price" type="number" style="width:100px" placeholder="0" />
      </div>
      <div>
        <label>до</label>
        <input v-model="filters.max_price" type="number" style="width:100px" placeholder="∞" />
      </div>
      <div style="flex:1">
        <label>Поиск по названию</label>
        <input v-model="filters.search" placeholder="Введите название..." @keyup.enter="applyFilters" />
      </div>
      <button class="btn btn-primary" @click="applyFilters">Найти</button>
      <button class="btn btn-secondary" @click="resetFilters">Сбросить</button>
    </div>

    <p style="color:#666;margin-bottom:12px">Найдено: {{ total }} товаров</p>

    <div v-if="loading" style="text-align:center;padding:40px;color:#999">Загрузка...</div>
    <div v-else class="grid">
      <div v-for="p in products" :key="p.id" class="card" style="display:flex;flex-direction:column">
        <router-link :to="`/product/${p.id}`" style="text-decoration:none;color:inherit">
          <h3 style="margin-bottom:6px;font-size:15px">{{ p.name }}</h3>
        </router-link>
        <div style="font-size:12px;color:#888;margin-bottom:6px">{{ p.type_name }} · {{ p.seller_name }}</div>
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px">
          <span style="color:#f39c12" v-if="p.avg_rating">★ {{ p.avg_rating }}</span>
          <span style="color:#999;font-size:12px" v-if="p.review_count">({{ p.review_count }})</span>
        </div>
        <div style="margin-top:auto">
          <div style="font-size:18px;font-weight:bold;color:#2c3e50">{{ p.price.toFixed(2) }} ₽</div>
          <div style="font-size:12px;color:#27ae60;margin:4px 0" v-if="p.stock_quantity > 0">В наличии: {{ p.stock_quantity }}</div>
          <div style="font-size:12px;color:#e74c3c;margin:4px 0" v-else>Нет в наличии</div>
          <button class="btn btn-primary" style="margin-top:8px;width:100%" @click="addToCart(p)" :disabled="p.stock_quantity === 0">
            В корзину
          </button>
        </div>
      </div>
    </div>

    <div v-if="pages() > 1" style="display:flex;gap:8px;justify-content:center;margin-top:24px">
      <button class="btn btn-secondary" @click="page--" :disabled="page === 1">←</button>
      <span style="padding:8px 12px">{{ page }} / {{ pages() }}</span>
      <button class="btn btn-secondary" @click="page++" :disabled="page >= pages()">→</button>
    </div>
  </div>
</template>
