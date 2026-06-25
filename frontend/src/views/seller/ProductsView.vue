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
    const { data } = await api.get('/product-types')
    types.value = data
    await loadProducts()
  } finally {
    loading.value = false
  }
})

async function loadProducts() {
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

function cancelForm() {
  showForm.value = false
  editTarget.value = null
  error.value = ''
}

async function save() {
  error.value = ''
  try {
    const payload = {
      type_id: Number(form.value.type_id),
      name: form.value.name,
      price: Number(form.value.price),
      stock_quantity: Number(form.value.stock_quantity),
    }
    if (editTarget.value) {
      await api.put(`/products/${editTarget.value.id}`, payload)
    } else {
      await api.post('/products', payload)
    }
    showForm.value = false
    editTarget.value = null
    await loadProducts()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка сохранения'
  }
}

async function remove(id) {
  if (!confirm('Удалить товар?')) return
  await api.delete(`/products/${id}`)
  await loadProducts()
}

function stockClass(qty) {
  if (qty === 0) return 'text-danger'
  if (qty <= 10) return 'text-warning'
  return 'text-success'
}
</script>

<template>
  <div>
    <div class="page-title">
      <h1>Мои товары</h1>
      <button class="btn btn-primary" @click="openCreate">+ Добавить товар</button>
    </div>

    <!-- Form -->
    <div v-if="showForm" class="card form-card">
      <h3 style="margin-bottom:18px">{{ editTarget ? 'Редактировать товар' : 'Новый товар' }}</h3>
      <form @submit.prevent="save">
        <div class="form-row">
          <div class="field">
            <label>Категория</label>
            <select v-model="form.type_id" required>
              <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
          <div class="field" style="flex:2">
            <label>Название товара</label>
            <input v-model="form.name" placeholder="Введите название" required />
          </div>
        </div>
        <div class="form-row">
          <div class="field">
            <label>Цена (₽)</label>
            <input v-model="form.price" type="number" step="0.01" min="0" placeholder="0.00" required />
          </div>
          <div class="field">
            <label>Остаток (шт.)</label>
            <input v-model="form.stock_quantity" type="number" min="0" placeholder="0" required />
          </div>
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary">{{ editTarget ? 'Сохранить' : 'Создать товар' }}</button>
          <button type="button" class="btn btn-ghost" @click="cancelForm">Отмена</button>
        </div>
      </form>
    </div>

    <!-- Table -->
    <div v-if="loading" class="empty-state">Загрузка...</div>
    <div v-else-if="!products.length" class="empty-state card">
      У вас пока нет товаров.
    </div>
    <div v-else class="card" style="padding:0;overflow:hidden">
      <table>
        <thead>
          <tr>
            <th>Название</th>
            <th>Категория</th>
            <th>Цена</th>
            <th>Остаток</th>
            <th>Рейтинг</th>
            <th style="width:100px">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id">
            <td>
              <router-link :to="`/product/${p.id}`" style="font-weight:500">{{ p.name }}</router-link>
            </td>
            <td>
              <span class="badge badge-gray">{{ p.type_name }}</span>
            </td>
            <td style="font-weight:600">{{ p.price.toFixed(2) }} ₽</td>
            <td>
              <span :class="stockClass(p.stock_quantity)" style="font-weight:600">{{ p.stock_quantity }}</span>
            </td>
            <td>
              <span v-if="p.avg_rating" style="color:#f59e0b;font-weight:600">★ {{ p.avg_rating }}</span>
              <span v-else class="muted">—</span>
            </td>
            <td>
              <div style="display:flex;gap:6px">
                <button class="btn btn-ghost btn-sm btn-icon" @click="openEdit(p)" title="Редактировать">✎</button>
                <button class="btn btn-danger btn-sm btn-icon" @click="remove(p.id)" title="Удалить">✕</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.form-card { margin-bottom: 18px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.field { display: flex; flex-direction: column; }
.field label { margin-top: 0; margin-bottom: 5px; }
.form-actions { display: flex; gap: 10px; margin-top: 18px; }
</style>
