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
    const [oRes, sRes] = await Promise.all([api.get('/orders'), api.get('/order-statuses')])
    orders.value = oRes.data
    statuses.value = sRes.data
  } finally {
    loading.value = false
  }
})

async function toggle(id) {
  if (selected.value?.id === id) { selected.value = null; return }
  const { data } = await api.get(`/orders/${id}`)
  selected.value = data
  error.value = ''
}

async function changeStatus(orderId, statusId) {
  if (!statusId) return
  error.value = ''
  try {
    await api.patch(`/orders/${orderId}/status`, { status_id: Number(statusId) })
    const [oRes] = await Promise.all([api.get('/orders')])
    orders.value = oRes.data
    if (selected.value?.id === orderId) {
      const { data } = await api.get(`/orders/${orderId}`)
      selected.value = data
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка смены статуса'
  }
}

function currentSortOrder(statusName) {
  return statuses.value.find(s => s.name === statusName)?.sort_order ?? 0
}

function availableNext(statusName) {
  const cur = currentSortOrder(statusName)
  return statuses.value.filter(s => s.sort_order > cur)
}

function statusClass(name) {
  if (name === 'Доставлен') return 'badge-green'
  if (name === 'Отменён') return 'badge-red'
  if (name === 'В доставке') return 'badge-purple'
  if (name === 'Собран') return 'badge-yellow'
  return 'badge-gray'
}
</script>

<template>
  <div>
    <h1 style="margin-bottom:22px">Входящие заказы</h1>

    <div v-if="loading" class="empty-state">Загрузка...</div>
    <div v-else-if="!orders.length" class="empty-state card">
      Заказов с вашими товарами пока нет
    </div>

    <div v-else>
      <div v-if="error" class="error" style="margin-bottom:14px">{{ error }}</div>

      <div class="order-list">
        <div v-for="o in orders" :key="o.id" class="card order-card">
          <!-- Header -->
          <div class="order-head">
            <div>
              <div class="order-num">Заказ #{{ o.id }}</div>
              <div class="muted text-sm" style="margin-top:2px">{{ new Date(o.order_date).toLocaleString('ru') }}</div>
              <div class="text-sm" style="margin-top:2px;color:#475569">{{ o.delivery_address }}</div>
            </div>
            <div class="order-actions">
              <span class="badge" :class="statusClass(o.status_name)">{{ o.status_name }}</span>

              <!-- Status selector (only if not final) -->
              <select
                v-if="!statuses.find(s => s.name === o.status_name)?.is_final"
                class="status-select"
                @change="e => { changeStatus(o.id, e.target.value); e.target.value = '' }">
                <option value="">Сменить статус...</option>
                <option
                  v-for="s in availableNext(o.status_name)"
                  :key="s.id"
                  :value="s.id">
                  {{ s.name }}
                </option>
              </select>

              <button class="btn btn-ghost btn-sm" @click="toggle(o.id)">
                {{ selected?.id === o.id ? 'Скрыть' : 'Детали' }}
              </button>
            </div>
          </div>

          <!-- Expanded items -->
          <div v-if="selected?.id === o.id" class="order-details">
            <table>
              <thead>
                <tr>
                  <th>Товар</th>
                  <th>Цена</th>
                  <th>Кол-во</th>
                  <th>Сумма</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in selected.items" :key="item.product_id">
                  <td style="font-weight:500">{{ item.product_name }}</td>
                  <td>{{ item.price_at_order.toFixed(2) }} ₽</td>
                  <td>{{ item.quantity }}</td>
                  <td><b>{{ (item.price_at_order * item.quantity).toFixed(2) }} ₽</b></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.order-list { display: flex; flex-direction: column; gap: 10px; }

.order-card { padding: 0; overflow: hidden; }

.order-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding: 16px 20px;
  flex-wrap: wrap;
}

.order-num { font-size: 14.5px; font-weight: 600; color: #1e293b; }

.order-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  flex-shrink: 0;
}

.status-select {
  width: 180px !important;
  margin: 0 !important;
  padding: 6px 10px !important;
  font-size: 13px !important;
}

.order-details {
  border-top: 1px solid #f1f5f9;
  padding: 14px 20px;
  background: #fafbfc;
}
.order-details th, .order-details td { padding: 8px 12px; }
</style>
