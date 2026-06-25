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

async function toggle(id) {
  if (selected.value?.id === id) { selected.value = null; return }
  const { data } = await api.get(`/orders/${id}`)
  selected.value = data
}

const STATUS_STEPS = ['Оформлен', 'Собран', 'В доставке', 'Доставлен']

function stepIndex(name) {
  const i = STATUS_STEPS.indexOf(name)
  return i >= 0 ? i : (name === 'Отменён' ? -1 : 0)
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
    <h1 style="margin-bottom:22px">Мои заказы</h1>

    <div v-if="loading" class="empty-state">Загрузка...</div>

    <div v-else-if="!orders.length" class="empty-state card">
      Заказов пока нет.
      <router-link to="/catalog" style="margin-top:12px;display:inline-block" class="btn btn-primary btn-sm">Перейти в каталог</router-link>
    </div>

    <div v-else class="order-list">
      <div v-for="o in orders" :key="o.id" class="card order-card">
        <!-- Order header -->
        <div class="order-head">
          <div class="order-id-block">
            <span class="order-num">Заказ #{{ o.id }}</span>
            <span class="order-date muted text-sm">{{ new Date(o.order_date).toLocaleString('ru') }}</span>
          </div>
          <div class="order-right">
            <span class="badge" :class="statusClass(o.status_name)">{{ o.status_name }}</span>
            <button class="btn btn-ghost btn-sm" @click="toggle(o.id)">
              {{ selected?.id === o.id ? 'Скрыть' : 'Детали' }}
            </button>
          </div>
        </div>

        <!-- Status progress (not for cancelled) -->
        <div v-if="o.status_name !== 'Отменён'" class="status-track">
          <div
            v-for="(step, idx) in STATUS_STEPS"
            :key="step"
            class="track-step"
            :class="{
              done: idx <= stepIndex(o.status_name) && o.status_name !== 'Отменён',
              active: idx === stepIndex(o.status_name)
            }">
            <div class="track-dot"></div>
            <div class="track-line" v-if="idx < STATUS_STEPS.length - 1"></div>
            <div class="track-label">{{ step }}</div>
          </div>
        </div>

        <!-- Expanded details -->
        <div v-if="selected?.id === o.id" class="order-details">
          <div class="detail-address">
            <span class="muted text-sm">Адрес доставки:</span>
            <span class="text-sm" style="margin-left:6px">{{ o.delivery_address }}</span>
          </div>
          <table class="order-items-table">
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
                <td>
                  <router-link :to="`/product/${item.product_id}`" style="font-weight:500">{{ item.product_name }}</router-link>
                </td>
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
</template>

<style scoped>
.order-list { display: flex; flex-direction: column; gap: 12px; }

.order-card { padding: 0; overflow: hidden; }

.order-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 20px;
  flex-wrap: wrap;
}
.order-id-block { display: flex; flex-direction: column; gap: 2px; }
.order-num { font-size: 14.5px; font-weight: 600; color: #1e293b; }
.order-date { }
.order-right { display: flex; align-items: center; gap: 10px; }

/* Progress track */
.status-track {
  display: flex;
  align-items: flex-start;
  padding: 0 20px 16px;
  gap: 0;
}
.track-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}
.track-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e2e8f0;
  border: 2px solid #e2e8f0;
  position: relative;
  z-index: 1;
  transition: background .2s;
}
.track-step.done .track-dot { background: #4f46e5; border-color: #4f46e5; }
.track-step.active .track-dot {
  background: #fff;
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79,70,229,.15);
}
.track-line {
  position: absolute;
  top: 4px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #e2e8f0;
}
.track-step.done .track-line { background: #4f46e5; }
.track-label {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 7px;
  white-space: nowrap;
  text-align: center;
}
.track-step.done .track-label { color: #4f46e5; font-weight: 500; }
.track-step.active .track-label { color: #4f46e5; font-weight: 600; }

/* Details */
.order-details {
  border-top: 1px solid #f1f5f9;
  padding: 16px 20px;
  background: #fafbfc;
}
.detail-address { margin-bottom: 14px; }
.order-items-table th, .order-items-table td { padding: 8px 12px; }
</style>
