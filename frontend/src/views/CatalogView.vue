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
const PAGE_SIZE = 20
const loading = ref(false)
const types = ref([])
const filters = ref({ type_id: '', min_price: '', max_price: '', search: '' })

onMounted(async () => {
  const { data } = await api.get('/product-types')
  types.value = data
  await load()
})

watch(page, load)

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: PAGE_SIZE }
    if (filters.value.type_id) params.type_id = filters.value.type_id
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

function apply() { page.value = 1; load() }
function reset() {
  filters.value = { type_id: '', min_price: '', max_price: '', search: '' }
  apply()
}

function addToCart(p) {
  if (!auth.isCustomer) { router.push('/login'); return }
  cart.add(p)
}

function stars(r) {
  if (!r) return ''
  const full = Math.round(r)
  return '★'.repeat(full) + '☆'.repeat(5 - full)
}

const pages = () => Math.ceil(total.value / PAGE_SIZE)
</script>

<template>
  <div>
    <!-- Filter bar -->
    <div class="filter-bar card">
      <div class="filter-search">
        <input
          v-model="filters.search"
          placeholder="Поиск товаров..."
          @keyup.enter="apply"
          class="search-input"
        />
      </div>
      <div class="filter-fields">
        <select v-model="filters.type_id" class="filter-select">
          <option value="">Все категории</option>
          <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
        <input v-model="filters.min_price" type="number" placeholder="Цена от" class="filter-price" />
        <input v-model="filters.max_price" type="number" placeholder="до" class="filter-price" />
        <button class="btn btn-primary btn-sm" @click="apply">Найти</button>
        <button class="btn btn-ghost btn-sm" @click="reset">Сбросить</button>
      </div>
    </div>

    <!-- Stats row -->
    <div class="stats-row">
      <span class="muted text-sm">Найдено: <b style="color:#1e293b">{{ total }}</b> товаров</span>
      <span v-if="loading" class="muted text-sm">Загрузка...</span>
    </div>

    <!-- Product grid -->
    <div v-if="!loading && products.length === 0" class="empty-state">
      Товары не найдены. <a @click.prevent="reset" href="#">Сбросить фильтры</a>
    </div>

    <div v-else class="grid">
      <div v-for="p in products" :key="p.id" class="product-card card">
        <div class="product-meta">
          <span class="badge badge-gray">{{ p.type_name }}</span>
          <span class="product-seller">{{ p.seller_name }}</span>
        </div>

        <router-link :to="`/product/${p.id}`" class="product-name">
          {{ p.name }}
        </router-link>

        <div class="product-rating" v-if="p.avg_rating">
          <span class="stars">{{ stars(p.avg_rating) }}</span>
          <span class="rating-val">{{ p.avg_rating }}</span>
          <span class="muted text-sm">({{ p.review_count }})</span>
        </div>

        <div class="product-footer">
          <div>
            <div class="product-price">{{ p.price.toFixed(2) }} ₽</div>
            <div class="stock-label" :class="p.stock_quantity > 0 ? 'in-stock' : 'no-stock'">
              {{ p.stock_quantity > 0 ? `В наличии: ${p.stock_quantity}` : 'Нет в наличии' }}
            </div>
          </div>
          <button
            class="btn btn-primary btn-sm"
            @click="addToCart(p)"
            :disabled="p.stock_quantity === 0">
            В корзину
          </button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pages() > 1" class="pagination">
      <button class="btn btn-ghost btn-sm" @click="page--" :disabled="page === 1">&#8592;</button>
      <span class="page-info">{{ page }} / {{ pages() }}</span>
      <button class="btn btn-ghost btn-sm" @click="page++" :disabled="page >= pages()">&#8594;</button>
    </div>
  </div>
</template>

<style scoped>
/* Filter bar */
.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
  padding: 14px 18px;
}
.filter-search { flex: 1; min-width: 200px; }
.search-input { margin: 0 !important; }
.filter-fields {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.filter-select {
  width: 160px !important;
  margin: 0 !important;
}
.filter-price {
  width: 100px !important;
  margin: 0 !important;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

/* Product card */
.product-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  transition: box-shadow .15s, transform .15s;
}
.product-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,.09);
  transform: translateY(-1px);
}

.product-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}
.product-seller {
  font-size: 11.5px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
}
.product-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.35;
  text-decoration: none;
}
.product-name:hover { color: #4f46e5; }

.product-rating {
  display: flex;
  align-items: center;
  gap: 5px;
}
.stars { color: #f59e0b; font-size: 12px; letter-spacing: -.5px; }
.rating-val { font-size: 12.5px; font-weight: 600; color: #475569; }

.product-footer {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-top: auto;
  gap: 8px;
}
.product-price {
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
}
.stock-label {
  font-size: 11.5px;
  margin-top: 2px;
}
.in-stock { color: #059669; }
.no-stock  { color: #dc2626; }

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 28px;
}
.page-info { font-size: 13px; color: #64748b; }
</style>
