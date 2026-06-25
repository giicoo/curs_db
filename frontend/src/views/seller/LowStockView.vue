<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/index.js'

const products = ref([])
const threshold = ref(10)
const loading = ref(false)

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

function urgency(qty) {
  if (qty === 0) return 'crit'
  if (qty <= 5) return 'warn'
  return 'low'
}
</script>

<template>
  <div>
    <div class="page-title">
      <div>
        <h1>Остатки товаров</h1>
        <p class="muted text-sm" style="margin-top:3px">Товары с количеством ниже порога</p>
      </div>
      <div class="threshold-ctrl">
        <label style="margin:0;white-space:nowrap">Порог:</label>
        <input v-model.number="threshold" type="number" min="0" class="threshold-inp" />
        <button class="btn btn-primary btn-sm" @click="load">Применить</button>
      </div>
    </div>

    <div v-if="loading" class="empty-state">Загрузка...</div>

    <div v-else-if="!products.length" class="empty-state card">
      Нет товаров с остатком &le; {{ threshold }}
    </div>

    <div v-else class="card" style="padding:0;overflow:hidden">
      <div class="list-header">
        <span class="muted text-sm">{{ products.length }} товаров требуют пополнения</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Товар</th>
            <th>Категория</th>
            <th>Цена</th>
            <th>Остаток</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id">
            <td>
              <router-link :to="`/product/${p.id}`" style="font-weight:500">{{ p.name }}</router-link>
            </td>
            <td><span class="badge badge-gray">{{ p.type_name }}</span></td>
            <td>{{ p.price.toFixed(2) }} ₽</td>
            <td>
              <span class="qty-badge" :class="`qty-${urgency(p.stock_quantity)}`">
                {{ p.stock_quantity }}
              </span>
            </td>
            <td>
              <span v-if="p.stock_quantity === 0" class="badge badge-red">Нет в наличии</span>
              <span v-else-if="p.stock_quantity <= 5" class="badge badge-yellow">Критически мало</span>
              <span v-else class="badge badge-gray">Мало</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.threshold-ctrl {
  display: flex;
  align-items: center;
  gap: 8px;
}
.threshold-inp {
  width: 72px !important;
  margin: 0 !important;
  text-align: center;
}
.list-header {
  padding: 10px 16px;
  border-bottom: 1px solid #f1f5f9;
  background: #f8fafc;
}
.qty-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 26px;
  padding: 0 8px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 700;
}
.qty-crit { background: #fef2f2; color: #dc2626; }
.qty-warn { background: #fffbeb; color: #b45309; }
.qty-low  { background: #f1f5f9; color: #475569; }
</style>
