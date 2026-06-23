<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/index.js'

const products = ref([])
const threshold = ref(10)
const loading = ref(true)

onMounted(() => load())

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/products/low-stock', { params: { threshold: threshold.value } })
    products.value = data
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px">
      <h1>Товары с низким остатком</h1>
      <div style="display:flex;align-items:center;gap:8px">
        <label style="margin:0;white-space:nowrap">Порог:</label>
        <input v-model.number="threshold" type="number" min="0" style="width:80px" />
        <button class="btn btn-primary" @click="load">Применить</button>
      </div>
    </div>

    <div v-if="loading" style="text-align:center;padding:40px;color:#999">Загрузка...</div>
    <div v-else class="card">
      <div v-if="products.length === 0" style="text-align:center;padding:30px;color:#999">
        Нет товаров с остатком ≤ {{ threshold }}
      </div>
      <table v-else>
        <thead>
          <tr><th>Название</th><th>Категория</th><th>Цена</th><th>Остаток</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id">
            <td><router-link :to="`/product/${p.id}`">{{ p.name }}</router-link></td>
            <td>{{ p.type_name }}</td>
            <td>{{ p.price.toFixed(2) }} ₽</td>
            <td>
              <span :style="{ color: p.stock_quantity === 0 ? '#e74c3c' : '#e67e22', fontWeight: 'bold' }">
                {{ p.stock_quantity }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
