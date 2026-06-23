<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/index.js'

const products = ref([])
const types = ref([])
const loading = ref(true)
const showForm = ref(false)
const editTarget = ref(null)
const error = ref('')

const form = ref({ type_id: '', name: '', price: '', stock_quantity: 0 })

onMounted(async () => {
  try {
    const [pRes, tRes] = await Promise.all([
      api.get('/catalog', { params: { page_size: 100 } }),
      api.get('/product-types'),
    ])
    types.value = tRes.data
    await loadMyProducts()
  } finally {
    loading.value = false
  }
})

async function loadMyProducts() {
  const { data: me } = await api.get('/auth/me')
  const { data } = await api.get('/catalog', {
    params: { seller_id: me.profile.id, page_size: 100 },
  })
  products.value = data.items
}

function openCreate() {
  editTarget.value = null
  form.value = { type_id: types.value[0]?.id || '', name: '', price: '', stock_quantity: 0 }
  error.value = ''
  showForm.value = true
}

function openEdit(p) {
  editTarget.value = p
  form.value = { type_id: p.type_id, name: p.name, price: p.price, stock_quantity: p.stock_quantity }
  error.value = ''
  showForm.value = true
}

async function saveProduct() {
  error.value = ''
  try {
    if (editTarget.value) {
      await api.put(`/products/${editTarget.value.id}`, {
        type_id: Number(form.value.type_id),
        name: form.value.name,
        price: Number(form.value.price),
        stock_quantity: Number(form.value.stock_quantity),
      })
    } else {
      await api.post('/products', {
        type_id: Number(form.value.type_id),
        name: form.value.name,
        price: Number(form.value.price),
        stock_quantity: Number(form.value.stock_quantity),
      })
    }
    showForm.value = false
    await loadMyProducts()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}

async function deleteProduct(id) {
  if (!confirm('Удалить товар?')) return
  await api.delete(`/products/${id}`)
  await loadMyProducts()
}
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h1>Мои товары</h1>
      <button class="btn btn-primary" @click="openCreate">+ Добавить товар</button>
    </div>

    <div v-if="showForm" class="card" style="margin-bottom:20px">
      <h3 style="margin-bottom:12px">{{ editTarget ? 'Редактировать товар' : 'Новый товар' }}</h3>
      <form @submit.prevent="saveProduct">
        <label>Категория</label>
        <select v-model="form.type_id" required>
          <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
        <label>Название</label>
        <input v-model="form.name" required />
        <label>Цена (₽)</label>
        <input v-model="form.price" type="number" step="0.01" min="0" required />
        <label>Остаток (шт)</label>
        <input v-model="form.stock_quantity" type="number" min="0" required />
        <div class="error" v-if="error">{{ error }}</div>
        <div style="display:flex;gap:8px;margin-top:12px">
          <button class="btn btn-primary" type="submit">Сохранить</button>
          <button class="btn btn-secondary" type="button" @click="showForm=false">Отмена</button>
        </div>
      </form>
    </div>

    <div v-if="loading" style="text-align:center;padding:40px;color:#999">Загрузка...</div>
    <div v-else class="card">
      <table>
        <thead>
          <tr><th>Название</th><th>Категория</th><th>Цена</th><th>Остаток</th><th>Рейтинг</th><th>Действия</th></tr>
        </thead>
        <tbody>
          <tr v-if="products.length === 0">
            <td colspan="6" style="text-align:center;color:#999;padding:20px">Товаров нет</td>
          </tr>
          <tr v-for="p in products" :key="p.id">
            <td><router-link :to="`/product/${p.id}`">{{ p.name }}</router-link></td>
            <td>{{ p.type_name }}</td>
            <td>{{ p.price.toFixed(2) }} ₽</td>
            <td>
              <span :style="{ color: p.stock_quantity > 10 ? '#27ae60' : p.stock_quantity > 0 ? '#e67e22' : '#e74c3c' }">
                {{ p.stock_quantity }}
              </span>
            </td>
            <td>{{ p.avg_rating ? `★ ${p.avg_rating}` : '—' }}</td>
            <td>
              <button class="btn btn-secondary" style="padding:4px 10px;margin-right:6px" @click="openEdit(p)">✎</button>
              <button class="btn btn-danger" style="padding:4px 10px" @click="deleteProduct(p.id)">✕</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
