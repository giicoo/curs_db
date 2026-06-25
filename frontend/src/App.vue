<script setup>
import { useAuthStore } from './stores/auth.js'
import { useCartStore } from './stores/cart.js'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const cart = useCartStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="topbar">
    <div class="topbar-inner">
      <router-link to="/catalog" class="logo">Маркетплейс</router-link>

      <nav class="nav">
        <router-link v-if="!auth.isSeller" to="/catalog" class="nav-link">Каталог</router-link>

        <template v-if="auth.isAuthenticated">
          <template v-if="auth.isCustomer">
            <router-link to="/cart" class="nav-link">
              Корзина
              <span v-if="cart.count" class="cart-pill">{{ cart.count }}</span>
            </router-link>
            <router-link to="/orders" class="nav-link">Заказы</router-link>
          </template>

          <template v-if="auth.isSeller">
            <router-link to="/seller/products" class="nav-link">Товары</router-link>
            <router-link to="/seller/orders" class="nav-link">Заказы</router-link>
            <router-link to="/seller/low-stock" class="nav-link">Остатки</router-link>
            <router-link to="/reports" class="nav-link">Аналитика</router-link>
          </template>

          <span class="nav-sep"></span>
          <span class="nav-user">{{ auth.user?.login }}</span>
          <button @click="logout" class="nav-link nav-exit">Выйти</button>
        </template>

        <template v-else>
          <router-link to="/login" class="nav-link">Войти</router-link>
          <router-link to="/register" class="btn btn-primary" style="margin-left:6px;padding:7px 14px;font-size:13px">Регистрация</router-link>
        </template>
      </nav>
    </div>
  </header>

  <main class="page">
    <router-view />
  </main>
</template>

<style>
/* ── Reset ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
* { margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
  background: #f8fafc;
  color: #1e293b;
  font-size: 14px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* ── Topbar ─────────────────────────────────────────── */
.topbar {
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 100;
}
.topbar-inner {
  max-width: 1220px;
  margin: 0 auto;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.logo {
  font-size: 16px;
  font-weight: 700;
  color: #4f46e5;
  text-decoration: none;
  letter-spacing: -.02em;
  flex-shrink: 0;
}
.nav {
  display: flex;
  align-items: center;
  gap: 1px;
}
.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 10px;
  border-radius: 7px;
  font-size: 13.5px;
  font-weight: 500;
  color: #64748b;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  transition: background .13s, color .13s;
  white-space: nowrap;
}
.nav-link:hover { background: #f1f5f9; color: #1e293b; }
.nav-link.router-link-active { color: #4f46e5; background: #eef2ff; }
.nav-sep { width: 1px; height: 18px; background: #e2e8f0; margin: 0 8px; }
.nav-user { font-size: 12.5px; color: #94a3b8; padding: 0 2px; }
.nav-exit { color: #94a3b8; }
.nav-exit:hover { color: #dc2626; background: #fef2f2; }
.cart-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  font-size: 11px;
  font-weight: 700;
  background: #4f46e5;
  color: #fff;
  border-radius: 9px;
}

/* ── Page ───────────────────────────────────────────── */
.page {
  max-width: 1220px;
  margin: 0 auto;
  padding: 28px 24px;
}

/* ── Typography ─────────────────────────────────────── */
h1 { font-size: 21px; font-weight: 700; color: #0f172a; letter-spacing: -.02em; }
h2 { font-size: 17px; font-weight: 600; color: #0f172a; }
h3 { font-size: 14.5px; font-weight: 600; color: #1e293b; }

/* ── Cards ──────────────────────────────────────────── */
.card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9edf2;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}

/* ── Buttons ────────────────────────────────────────── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 13.5px;
  font-weight: 500;
  font-family: inherit;
  line-height: 1;
  text-decoration: none;
  white-space: nowrap;
  transition: background .13s, opacity .13s, transform .07s;
}
.btn:active:not(:disabled) { transform: scale(.98); }
.btn:disabled { opacity: .48; cursor: not-allowed; }

.btn-primary  { background: #4f46e5; color: #fff; }
.btn-primary:hover:not(:disabled)  { background: #4338ca; }

.btn-secondary { background: #f1f5f9; color: #475569; }
.btn-secondary:hover:not(:disabled) { background: #e2e8f0; color: #1e293b; }

.btn-danger  { background: #dc2626; color: #fff; }
.btn-danger:hover:not(:disabled)  { background: #b91c1c; }

.btn-success { background: #059669; color: #fff; }
.btn-success:hover:not(:disabled) { background: #047857; }

.btn-ghost {
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
}
.btn-ghost:hover:not(:disabled) { background: #f8fafc; color: #1e293b; }

.btn-sm { padding: 5px 11px; font-size: 12.5px; border-radius: 6px; }
.btn-icon { padding: 7px; }

/* ── Forms ──────────────────────────────────────────── */
label {
  display: block;
  font-size: 12.5px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 5px;
  margin-top: 16px;
}
label:first-of-type { margin-top: 0; }

input, select, textarea {
  display: block;
  width: 100%;
  padding: 9px 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13.5px;
  color: #1e293b;
  background: #fff;
  outline: none;
  font-family: inherit;
  transition: border-color .14s, box-shadow .14s;
}
input:focus, select:focus, textarea:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99,102,241,.13);
}
input::placeholder, textarea::placeholder { color: #b0bac7; }
textarea { resize: vertical; min-height: 80px; }

.error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  font-size: 12.5px;
  padding: 8px 12px;
  border-radius: 7px;
  margin-top: 10px;
}

/* ── Tables ─────────────────────────────────────────── */
table { width: 100%; border-collapse: collapse; }
thead th {
  font-size: 11.5px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: .05em;
  padding: 9px 14px;
  border-bottom: 1px solid #e9edf2;
  text-align: left;
  background: #f8fafc;
}
thead th:first-child { border-radius: 8px 0 0 0; }
thead th:last-child  { border-radius: 0 8px 0 0; }
tbody td {
  padding: 11px 14px;
  font-size: 13.5px;
  border-bottom: 1px solid #f1f5f9;
  color: #1e293b;
  vertical-align: middle;
}
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover td { background: #fafbfc; }

/* ── Badges ─────────────────────────────────────────── */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 9px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}
.badge-blue   { background: #eef2ff; color: #4f46e5; }
.badge-green  { background: #ecfdf5; color: #059669; }
.badge-red    { background: #fef2f2; color: #dc2626; }
.badge-yellow { background: #fffbeb; color: #b45309; }
.badge-gray   { background: #f1f5f9; color: #64748b; }
.badge-purple { background: #f5f3ff; color: #7c3aed; }

/* ── Grid ───────────────────────────────────────────── */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 14px;
}

/* ── Misc helpers ───────────────────────────────────── */
.page-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
  gap: 12px;
  flex-wrap: wrap;
}
.muted { color: #94a3b8; }
.text-sm { font-size: 12.5px; }
.text-danger { color: #dc2626; }
.text-success { color: #059669; }
.text-warning { color: #b45309; }
a { color: #4f46e5; text-decoration: none; }
a:hover { text-decoration: underline; }

.empty-state {
  text-align: center;
  padding: 56px 20px;
  color: #94a3b8;
  font-size: 14px;
}
.empty-state p { margin-top: 6px; }
</style>
