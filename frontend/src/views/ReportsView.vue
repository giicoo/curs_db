<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import { useAuthStore } from '../stores/auth.js'
import api from '../api/index.js'

Chart.register(...registerables)

const auth = useAuthStore()

// Charts
const statusChart = ref(null)
const topChart = ref(null)
const activityChart = ref(null)
let chartInstances = {}

// Data
const statusData = ref([])
const topData = ref([])
const activityData = ref([])
const salesData = ref([])

// Filters
const salesFrom = ref('')
const salesTo = ref('')
const salesGroupBy = ref('product')
const topLimit = ref(10)
const actFrom = ref('')
const actTo = ref('')
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([loadStatus(), loadTop(), loadActivity()])
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  Object.values(chartInstances).forEach((c) => c.destroy())
})

async function loadStatus() {
  const { data } = await api.get('/reports/order-status-distribution')
  statusData.value = data
  await nextTick()
  renderStatusChart()
}

async function loadTop() {
  const { data } = await api.get('/reports/top-products', { params: { limit: topLimit.value } })
  topData.value = data
  await nextTick()
  renderTopChart()
}

async function loadActivity() {
  const params = {}
  if (actFrom.value) params.from = actFrom.value
  if (actTo.value) params.to = actTo.value
  const { data } = await api.get('/reports/customer-activity', { params })
  activityData.value = data
  await nextTick()
  renderActivityChart()
}

async function loadSales() {
  const params = { group_by: salesGroupBy.value }
  if (salesFrom.value) params.from = salesFrom.value
  if (salesTo.value) params.to = salesTo.value
  const { data } = await api.get('/reports/sales', { params })
  salesData.value = data
}

function destroyChart(key) {
  if (chartInstances[key]) { chartInstances[key].destroy(); delete chartInstances[key] }
}

function renderStatusChart() {
  destroyChart('status')
  if (!statusChart.value || !statusData.value.length) return
  chartInstances.status = new Chart(statusChart.value, {
    type: 'doughnut',
    data: {
      labels: statusData.value.map((d) => d.status_name),
      datasets: [{
        data: statusData.value.map((d) => d.order_count),
        backgroundColor: ['#3498db', '#f39c12', '#9b59b6', '#27ae60', '#e74c3c'],
      }],
    },
    options: { plugins: { legend: { position: 'right' } } },
  })
}

function renderTopChart() {
  destroyChart('top')
  if (!topChart.value || !topData.value.length) return
  chartInstances.top = new Chart(topChart.value, {
    type: 'bar',
    data: {
      labels: topData.value.map((d) => d.name.length > 20 ? d.name.slice(0, 20) + '…' : d.name),
      datasets: [{
        label: 'Выручка (₽)',
        data: topData.value.map((d) => d.total_revenue),
        backgroundColor: '#3498db',
      }],
    },
    options: {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: { x: { ticks: { callback: (v) => v.toLocaleString('ru') } } },
    },
  })
}

function renderActivityChart() {
  destroyChart('activity')
  if (!activityChart.value || !activityData.value.length) return
  chartInstances.activity = new Chart(activityChart.value, {
    type: 'bar',
    data: {
      labels: activityData.value.map((d) => d.customer_name),
      datasets: [{
        label: 'Потрачено (₽)',
        data: activityData.value.map((d) => d.total_spent),
        backgroundColor: '#27ae60',
      }],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: { y: { ticks: { callback: (v) => v.toLocaleString('ru') } } },
    },
  })
}
</script>

<template>
  <div>
    <h1 style="margin-bottom:24px">Аналитика</h1>
    <div v-if="loading" style="text-align:center;padding:40px;color:#999">Загрузка...</div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px" class="report-grid">
      <!-- Status distribution -->
      <div class="card">
        <h3 style="margin-bottom:16px">Распределение заказов по статусам</h3>
        <canvas ref="statusChart" height="220"></canvas>
        <div v-if="!statusData.length && !loading" style="text-align:center;color:#999;padding:20px">Нет данных</div>
      </div>

      <!-- Top products -->
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px">
          <h3>Топ товаров по выручке</h3>
          <div style="display:flex;gap:6px;align-items:center">
            <input v-model.number="topLimit" type="number" min="1" max="50" style="width:60px" />
            <button class="btn btn-primary" style="padding:6px 12px" @click="loadTop">Обновить</button>
          </div>
        </div>
        <canvas ref="topChart" height="220"></canvas>
        <div v-if="!topData.length && !loading" style="text-align:center;color:#999;padding:20px">Нет данных</div>
      </div>
    </div>

    <!-- Customer activity (only for non-seller or admin) -->
    <div class="card" style="margin-bottom:20px" v-if="!auth.isSeller">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px">
        <h3>Активность покупателей</h3>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <input v-model="actFrom" type="date" style="width:140px" />
          <span>—</span>
          <input v-model="actTo" type="date" style="width:140px" />
          <button class="btn btn-primary" style="padding:6px 12px" @click="loadActivity">Применить</button>
        </div>
      </div>
      <canvas ref="activityChart" height="140"></canvas>
      <div v-if="!activityData.length && !loading" style="text-align:center;color:#999;padding:20px">Нет данных</div>
    </div>

    <!-- Sales report -->
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px">
        <h3>Отчёт по продажам</h3>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <input v-model="salesFrom" type="date" style="width:140px" />
          <span>—</span>
          <input v-model="salesTo" type="date" style="width:140px" />
          <select v-model="salesGroupBy" style="width:130px">
            <option value="product">По товарам</option>
            <option value="type">По категориям</option>
            <option value="seller">По продавцам</option>
          </select>
          <button class="btn btn-primary" style="padding:6px 12px" @click="loadSales">Получить</button>
        </div>
      </div>
      <div v-if="salesData.length">
        <table>
          <thead>
            <tr>
              <th>Название</th>
              <th>Продано (шт)</th>
              <th>Кол-во заказов</th>
              <th>Выручка (₽)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in salesData" :key="row.group_id">
              <td>{{ row.group_name }}</td>
              <td>{{ row.total_quantity }}</td>
              <td>{{ row.order_count }}</td>
              <td>{{ row.total_revenue.toLocaleString('ru', {minimumFractionDigits:2}) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else style="text-align:center;color:#999;padding:20px">
        Выберите период и нажмите «Получить»
      </div>
    </div>
  </div>
</template>

<style scoped>
@media (max-width: 768px) {
  .report-grid { grid-template-columns: 1fr !important; }
}
</style>
