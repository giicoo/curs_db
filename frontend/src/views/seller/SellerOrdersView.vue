<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/index.js'

const orders = ref([])
const statuses = ref([])
const selected = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const [oRes, sRes] = await Promise.all([
      api.get('/orders'),
      api.get('/order-statuses'),
    ])
    orders.value = oRes.data
    statuses.value = sRes.data
  } finally {
    loading.value = false
  }
})

async function openOrder(id) {
  const { data } = await api.get(`/orders/${id}`)
  selected.value = data
  error.value = ''
}

async function updateStatus(orderId, statusId) {
  error.value = ''
  try {
    await api.patch(`/orders/${orderId}/status`, { status_id: Number(statusId) })
    const { data } = await api.get('/orders')
    orders.value = data
    if (selected.value?.id === orderId) {
      const { data: detail } = await api.get(`/orders/${orderId}`)
      selected.value = detail
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка смены статуса'
  }
}

function availableStatuses(currentSortOrder) {
  return statuses.value.filter((s) => s.sort_order > currentSortOrder)
}

function statusBadge(name) {
  const map = { 'Доставлен': 'badge-green', 'Отменён': 'badge-red' }
  return map[name] || 'badge-blue'
}
</script>

<template>
  <div>
    <h1 style="margin-bottom:20px">Входящие заказы</h1>

    <div v-if="loading" style="text-align:center;padding:40px;color:#999">Загрузка...</div>
    <div v-else-if="orders.length === 0" style="text-align:center;padding:60px;color:#999">Заказов пока нет</div>
    <div v-else>
      <div v-if="error" class="error" style="margin-bottom:12px;padding:8px;background:#fdedec;border-radius:6px">{{ error }}</div>
      <div class="card" v-for="o in orders" :key="o.id" style="margin-bottom:12px">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
          <div>
            <strong>Заказ #{{ o.id }}</strong>
            <div style="font-size:13px;color:#888;margin-top:2px">{{ new Date(o.order_date).toLocaleString('ru') }}</div>
            <div style="font-size:13px;margin-top:2px">{{ o.delivery_address }}</div>
          </div>
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
            <span class="badge" :class="statusBadge(o.status_name)">{{ o.status_name }}</span>
            <button class="btn btn-secondary" style="padding:6px 12px" @click="openOrder(o.id)">Детали</button>
          </div>
        </div>

        <div v-if="selected?.id === o.id" style="margin-top:16px;border-top:1px solid #eee;padding-top:12px">
          <table style="margin-bottom:12px">
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

          <div v-if="!selected.is_final" style="display:flex;align-items:center;gap:8px">
            <span style="font-size:13px">Сменить статус:</span>
            <select
              style="width:180px"
              @change="(e) => { updateStatus(o.id, e.target.value); e.target.value = '' }"
            >
              <option value="">Выберите статус</option>
              <option
                v-for="s in availableStatuses(statuses.find(st=>st.name===o.status_name)?.sort_order||0)"
                :key="s.id"
                :value="s.id"
              >{{ s.name }}</option>
            </select>
          </div>
          <div v-else style="color:#888;font-size:13px">Заказ в финальном статусе</div>
        </div>
      </div>
    </div>
  </div>
</template>
