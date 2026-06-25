<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { Chart, registerables } from 'chart.js'
import { useAuthStore } from '../stores/auth.js'
import api from '../api/index.js'

Chart.register(...registerables)

const auth = useAuthStore()

const revenueChartEl = ref(null)
const statusChartEl = ref(null)
const topChartEl = ref(null)
const secondaryChartEl = ref(null)

let charts = {}

const revenueData = ref([])
const statusData = ref([])
const topData = ref([])
const secondaryData = ref([])
const salesData = ref([])
const salesLoading = ref(false)

const salesFrom = ref('')
const salesTo = ref('')
const salesGroupBy = ref('product')
const loading = ref(true)

const COLORS = [
  '#6366f1', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#06b6d4', '#f97316', '#84cc16', '#ec4899', '#14b8a6',
]

const currentMonth = computed(() => {
  if (!revenueData.value.length) return { revenue: 0, order_count: 0, units_sold: 0 }
  return revenueData.value[revenueData.value.length - 1]
})

const prevMonth = computed(() => {
  if (revenueData.value.length < 2) return { revenue: 0 }
  return revenueData.value[revenueData.value.length - 2]
})

const revDelta = computed(() => {
  const c = currentMonth.value.revenue
  const p = prevMonth.value.revenue
  if (!p) return null
  return ((c - p) / p * 100).toFixed(1)
})

const avgCheck = computed(() => {
  const { revenue, order_count } = currentMonth.value
  return order_count > 0 ? revenue / order_count : 0
})

function fmt(v) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency', currency: 'RUB', maximumFractionDigits: 0,
  }).format(v)
}

function monthLabel(m) {
  const [y, mo] = m.split('-')
  const names = ['янв','фев','мар','апр','май','июн','июл','авг','сен','окт','ноя','дек']
  return names[+mo - 1] + " '" + y.slice(2)
}

function kill(key) {
  if (charts[key]) { charts[key].destroy(); delete charts[key] }
}

function renderRevenue() {
  kill('revenue')
  if (!revenueChartEl.value || !revenueData.value.length) return
  const labels = revenueData.value.map(d => monthLabel(d.month))
  charts.revenue = new Chart(revenueChartEl.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Выручка',
          data: revenueData.value.map(d => d.revenue),
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99,102,241,0.08)',
          fill: true,
          tension: 0.45,
          pointBackgroundColor: '#6366f1',
          pointRadius: 3,
          pointHoverRadius: 6,
          yAxisID: 'y',
        },
        {
          label: 'Заказов',
          data: revenueData.value.map(d => d.order_count),
          borderColor: '#10b981',
          backgroundColor: 'transparent',
          tension: 0.45,
          borderDash: [5, 3],
          pointBackgroundColor: '#10b981',
          pointRadius: 3,
          pointHoverRadius: 6,
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: { usePointStyle: true, pointStyle: 'circle', padding: 16, font: { size: 12 } },
        },
        tooltip: {
          callbacks: {
            label: ctx =>
              ctx.datasetIndex === 0
                ? '  ' + fmt(ctx.raw)
                : '  ' + ctx.raw + ' заказов',
          },
        },
      },
      scales: {
        y: {
          position: 'left',
          ticks: {
            callback: v => v >= 1000 ? (v / 1000).toFixed(0) + 'k ₽' : v + ' ₽',
            font: { size: 11 },
          },
          grid: { color: '#f1f5f9' },
        },
        y1: {
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { callback: v => v + ' зак.', font: { size: 11 } },
        },
        x: { grid: { display: false }, ticks: { font: { size: 11 } } },
      },
    },
  })
}

function renderStatus() {
  kill('status')
  if (!statusChartEl.value || !statusData.value.length) return
  charts.status = new Chart(statusChartEl.value, {
    type: 'doughnut',
    data: {
      labels: statusData.value.map(d => d.status_name),
      datasets: [{
        data: statusData.value.map(d => d.order_count),
        backgroundColor: COLORS,
        borderWidth: 0,
        hoverOffset: 8,
      }],
    },
    options: {
      cutout: '68%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { usePointStyle: true, pointStyle: 'circle', padding: 14, font: { size: 12 } },
        },
        tooltip: {
          callbacks: { label: ctx => `  ${ctx.label}: ${ctx.raw}` },
        },
      },
    },
  })
}

function renderTop() {
  kill('top')
  if (!topChartEl.value || !topData.value.length) return
  charts.top = new Chart(topChartEl.value, {
    type: 'bar',
    data: {
      labels: topData.value.map(d => d.name.length > 24 ? d.name.slice(0, 24) + '…' : d.name),
      datasets: [{
        data: topData.value.map(d => d.total_revenue),
        backgroundColor: COLORS.map(c => c + 'cc'),
        borderColor: COLORS,
        borderWidth: 1,
        borderRadius: 4,
      }],
    },
    options: {
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => '  ' + fmt(ctx.raw) } },
      },
      scales: {
        x: {
          ticks: { callback: v => v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v, font: { size: 11 } },
          grid: { color: '#f1f5f9' },
        },
        y: { grid: { display: false }, ticks: { font: { size: 11 } } },
      },
    },
  })
}

function renderSecondary() {
  kill('secondary')
  if (!secondaryChartEl.value || !secondaryData.value.length) return

  if (auth.isSeller) {
    charts.secondary = new Chart(secondaryChartEl.value, {
      type: 'doughnut',
      data: {
        labels: secondaryData.value.map(d => d.group_name),
        datasets: [{
          data: secondaryData.value.map(d => d.total_revenue),
          backgroundColor: COLORS,
          borderWidth: 0,
          hoverOffset: 8,
        }],
      },
      options: {
        cutout: '62%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { usePointStyle: true, pointStyle: 'circle', padding: 14, font: { size: 12 } },
          },
          tooltip: { callbacks: { label: ctx => `  ${ctx.label}: ${fmt(ctx.raw)}` } },
        },
      },
    })
  } else {
    charts.secondary = new Chart(secondaryChartEl.value, {
      type: 'bar',
      data: {
        labels: secondaryData.value.map(d => d.customer_name),
        datasets: [{
          label: 'Потрачено',
          data: secondaryData.value.map(d => d.total_spent),
          backgroundColor: '#6366f1aa',
          borderColor: '#6366f1',
          borderWidth: 1,
          borderRadius: 4,
        }],
      },
      options: {
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: ctx => '  ' + fmt(ctx.raw) } },
        },
        scales: {
          y: {
            ticks: { callback: v => (v / 1000).toFixed(0) + 'k', font: { size: 11 } },
            grid: { color: '#f1f5f9' },
          },
          x: { grid: { display: false }, ticks: { font: { size: 11 } } },
        },
      },
    })
  }
}

async function loadAll() {
  loading.value = true
  try {
    const requests = [
      api.get('/reports/revenue-by-month', { params: { months: 12 } }),
      api.get('/reports/order-status-distribution'),
      api.get('/reports/top-products', { params: { limit: 8 } }),
      auth.isSeller
        ? api.get('/reports/sales', { params: { group_by: 'type' } })
        : api.get('/reports/customer-activity', { params: { limit: 10 } }),
    ]
    const [r1, r2, r3, r4] = await Promise.all(requests)
    revenueData.value = r1.data
    statusData.value = r2.data
    topData.value = r3.data
    secondaryData.value = r4.data
  } finally {
    loading.value = false
  }

  await nextTick()
  renderRevenue()
  renderStatus()
  renderTop()
  renderSecondary()
}

async function loadSales() {
  salesLoading.value = true
  try {
    const params = { group_by: salesGroupBy.value }
    if (salesFrom.value) params.from = salesFrom.value
    if (salesTo.value) params.to = salesTo.value
    const { data } = await api.get('/reports/sales', { params })
    salesData.value = data
  } finally {
    salesLoading.value = false
  }
}

onMounted(loadAll)
onUnmounted(() => Object.values(charts).forEach(c => c.destroy()))
</script>

<template>
  <div class="rp">
    <div class="rp-head">
      <div>
        <h1 class="rp-title">Аналитика</h1>
        <p class="rp-sub">{{ auth.isSeller ? 'Показатели вашего магазина' : 'Показатели платформы' }}</p>
      </div>
    </div>

    <div v-if="loading" class="rp-loader">Загрузка данных...</div>

    <template v-else>
      <!-- KPI row -->
      <div class="kpi-row">
        <div class="kpi-card">
          <div class="kpi-ico" style="background:#ede9fe;color:#6366f1">₽</div>
          <div>
            <div class="kpi-lbl">Выручка (тек. месяц)</div>
            <div class="kpi-val">{{ fmt(currentMonth.revenue) }}</div>
            <div v-if="revDelta !== null"
                 class="kpi-delta"
                 :class="Number(revDelta) >= 0 ? 'delta-up' : 'delta-dn'">
              {{ Number(revDelta) >= 0 ? '↑' : '↓' }} {{ Math.abs(Number(revDelta)) }}% vs прошлый мес.
            </div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-ico" style="background:#dcfce7;color:#10b981">#</div>
          <div>
            <div class="kpi-lbl">Заказов (тек. месяц)</div>
            <div class="kpi-val">{{ currentMonth.order_count }}</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-ico" style="background:#fef3c7;color:#f59e0b">~</div>
          <div>
            <div class="kpi-lbl">Средний чек</div>
            <div class="kpi-val">{{ fmt(avgCheck) }}</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-ico" style="background:#fce7f3;color:#ec4899">↑</div>
          <div>
            <div class="kpi-lbl">Продано единиц (мес.)</div>
            <div class="kpi-val">{{ currentMonth.units_sold ?? 0 }}</div>
          </div>
        </div>
      </div>

      <!-- Revenue + Status -->
      <div class="grid-2-1">
        <div class="c-card">
          <div class="c-head">
            <h3>Выручка по месяцам</h3>
            <span class="badge">12 мес.</span>
          </div>
          <canvas ref="revenueChartEl" style="max-height:220px"></canvas>
        </div>
        <div class="c-card">
          <div class="c-head"><h3>Статусы заказов</h3></div>
          <div class="c-center">
            <canvas ref="statusChartEl" style="max-height:220px;max-width:260px"></canvas>
          </div>
          <div v-if="!statusData.length" class="c-empty">Нет данных</div>
        </div>
      </div>

      <!-- Top products + Category/Activity -->
      <div class="grid-1-1">
        <div class="c-card">
          <div class="c-head">
            <h3>Топ товаров по выручке</h3>
            <span class="badge">{{ topData.length }} поз.</span>
          </div>
          <canvas ref="topChartEl" style="max-height:240px"></canvas>
          <div v-if="!topData.length" class="c-empty">Нет данных</div>
        </div>
        <div class="c-card">
          <div class="c-head">
            <h3>{{ auth.isSeller ? 'Выручка по категориям' : 'Активность покупателей' }}</h3>
          </div>
          <div class="c-center">
            <canvas ref="secondaryChartEl" style="max-height:240px;max-width:300px"></canvas>
          </div>
          <div v-if="!secondaryData.length" class="c-empty">Нет данных</div>
        </div>
      </div>

      <!-- Sales table -->
      <div class="c-card">
        <div class="c-head" style="flex-wrap:wrap;gap:10px">
          <h3>Детальный отчёт по продажам</h3>
          <div class="tbl-filters">
            <input v-model="salesFrom" type="date" class="f-in" />
            <span style="color:#94a3b8">—</span>
            <input v-model="salesTo" type="date" class="f-in" />
            <select v-model="salesGroupBy" class="f-sel">
              <option value="product">По товарам</option>
              <option value="type">По категориям</option>
              <option v-if="!auth.isSeller" value="seller">По продавцам</option>
            </select>
            <button class="f-btn" @click="loadSales" :disabled="salesLoading">
              {{ salesLoading ? '...' : 'Получить' }}
            </button>
          </div>
        </div>

        <div v-if="salesData.length" class="tbl-wrap">
          <table class="rp-tbl">
            <thead>
              <tr>
                <th style="width:36px">#</th>
                <th>Название</th>
                <th>Продано (шт)</th>
                <th>Заказов</th>
                <th>Выручка</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in salesData" :key="row.group_id">
                <td class="rank">{{ i + 1 }}</td>
                <td>{{ row.group_name }}</td>
                <td>{{ row.total_quantity }}</td>
                <td>{{ row.order_count }}</td>
                <td class="money">{{ fmt(row.total_revenue) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="c-empty" style="padding:28px">
          Выберите период и нажмите «Получить»
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.rp { display: flex; flex-direction: column; gap: 18px; }

.rp-head { margin-bottom: 2px; }
.rp-title { font-size: 22px; font-weight: 700; color: #0f172a; }
.rp-sub { font-size: 13px; color: #64748b; margin-top: 3px; }

.rp-loader {
  text-align: center; padding: 72px;
  color: #94a3b8; font-size: 14px; letter-spacing: .02em;
}

/* KPI */
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }

.kpi-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.kpi-ico {
  width: 42px; height: 42px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 17px; font-weight: 700;
  flex-shrink: 0;
}

.kpi-lbl { font-size: 11px; color: #64748b; margin-bottom: 4px; text-transform: uppercase; letter-spacing: .04em; }
.kpi-val { font-size: 19px; font-weight: 700; color: #0f172a; line-height: 1.2; }
.kpi-delta { font-size: 11px; margin-top: 5px; }
.delta-up { color: #10b981; }
.delta-dn { color: #ef4444; }

/* Chart layout */
.grid-2-1 { display: grid; grid-template-columns: 2fr 1fr; gap: 14px; }
.grid-1-1 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

.c-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
}

.c-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.c-head h3 { font-size: 14px; font-weight: 600; color: #0f172a; }

.badge {
  font-size: 11px;
  background: #f1f5f9;
  color: #475569;
  padding: 2px 9px;
  border-radius: 20px;
}

.c-center { display: flex; justify-content: center; align-items: center; }
.c-empty { text-align: center; color: #94a3b8; font-size: 13px; padding: 16px; }

/* Sales table */
.tbl-filters {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.f-in {
  padding: 6px 10px !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 6px !important;
  font-size: 13px !important;
  width: 128px !important;
  margin: 0 !important;
  box-shadow: none !important;
}
.f-sel {
  padding: 6px 10px !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 6px !important;
  font-size: 13px !important;
  width: 150px !important;
  margin: 0 !important;
  box-shadow: none !important;
}
.f-btn {
  padding: 6px 16px;
  background: #6366f1;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
}
.f-btn:hover:not(:disabled) { background: #4f46e5; }
.f-btn:disabled { opacity: .6; cursor: not-allowed; }

.tbl-wrap { overflow-x: auto; margin-top: 4px; }
.rp-tbl { width: 100%; border-collapse: collapse; }
.rp-tbl th {
  font-size: 11px; font-weight: 600; color: #64748b;
  text-transform: uppercase; letter-spacing: .04em;
  padding: 8px 12px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
}
.rp-tbl td {
  padding: 10px 12px;
  font-size: 13px;
  color: #1e293b;
  border-bottom: 1px solid #f1f5f9;
}
.rp-tbl tbody tr:last-child td { border-bottom: none; }
.rp-tbl tbody tr:hover td { background: #f8fafc; }
.rank { color: #94a3b8 !important; font-size: 12px !important; }
.money { font-weight: 600 !important; }

@media (max-width: 900px) {
  .kpi-row { grid-template-columns: 1fr 1fr; }
  .grid-2-1 { grid-template-columns: 1fr; }
  .grid-1-1 { grid-template-columns: 1fr; }
}
@media (max-width: 520px) {
  .kpi-row { grid-template-columns: 1fr; }
}
</style>
