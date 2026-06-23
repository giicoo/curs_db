<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'

const orders = ref([])
const selected = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get('/orders')
    orders.value = data
  } finally {
    loading.value = false
  }
})

async function openOrder(id) {
  const { data } = await api.get(`/orders/${id}`)
  selected.value = data
}

function statusBadge(name) {
  const map = { 'Доставлен': 'badge-green', 'Отменён': 'badge-red' }
  return map[name] || 'badge-blue'
}
</script>

<template>
  <div>
    <h1 style="margin-bottom:20px">Мои заказы</h1>

    <div v-if="loading" style="text-align:center;padding:40px;color:#999">Загрузка...</div>
    <div v-else-if="orders.length === 0" style="text-align:center;padding:60px;color:#999">
      Заказов пока нет. <router-link to="/catalog">Перейти в каталог</router-link>
    </div>
    <div v-else>
      <div class="card" style="margin-bottom:16px" v-for="o in orders" :key="o.id">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
          <div>
            <strong>Заказ #{{ o.id }}</strong>
            <div style="font-size:13px;color:#888;margin-top:2px">{{ new Date(o.order_date).toLocaleString('ru') }}</div>
            <div style="font-size:13px;margin-top:2px">{{ o.delivery_address }}</div>
          </div>
          <div style="display:flex;align-items:center;gap:12px">
            <span class="badge" :class="statusBadge(o.status_name)">{{ o.status_name }}</span>
            <button class="btn btn-secondary" @click="openOrder(o.id)">Подробнее</button>
          </div>
        </div>

        <div v-if="selected?.id === o.id" style="margin-top:16px;border-top:1px solid #eee;padding-top:16px">
          <table>
            <thead><tr><th>Товар</th><th>Цена</th><th>Кол-во</th><th>Сумма</th></tr></thead>
            <tbody>
              <tr v-for="item in selected.items" :key="item.product_id">
                <td>{{ item.product_name }}</td>
                <td>{{ item.price_at_order.toFixed(2) }} ₽</td>
                <td>{{ item.quantity }}</td>
                <td>{{ (item.price_at_order * item.quantity).toFixed(2) }} ₽</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
