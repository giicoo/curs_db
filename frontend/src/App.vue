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
  <nav class="navbar">
    <router-link to="/catalog" class="brand">Маркетплейс</router-link>
    <div class="nav-links">
      <router-link to="/catalog">Каталог</router-link>
      <template v-if="auth.isAuthenticated">
        <template v-if="auth.isCustomer">
          <router-link to="/cart">Корзина ({{ cart.count }})</router-link>
          <router-link to="/orders">Мои заказы</router-link>
        </template>
        <template v-if="auth.isSeller">
          <router-link to="/seller/products">Мои товары</router-link>
          <router-link to="/seller/orders">Заказы</router-link>
          <router-link to="/seller/low-stock">Остатки</router-link>
        </template>
        <router-link to="/reports">Аналитика</router-link>
        <span class="username">{{ auth.user?.login }}</span>
        <button @click="logout" class="btn-link">Выйти</button>
      </template>
      <template v-else>
        <router-link to="/login">Войти</router-link>
        <router-link to="/register">Регистрация</router-link>
      </template>
    </div>
  </nav>
  <main class="container">
    <router-view />
  </main>
</template>

<style>
.navbar {
  background: #2c3e50;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.navbar a, .navbar .btn-link, .navbar .username { color: #ecf0f1; text-decoration: none; font-size: 14px; margin-left: 16px; }
.navbar a.router-link-active { color: #3498db; }
.navbar .brand { font-size: 20px; font-weight: bold; color: white; margin-left: 0; }
.btn-link { background: none; border: none; cursor: pointer; padding: 0; }
.container { max-width: 1200px; margin: 0 auto; padding: 24px 16px; }
.card { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
.btn { display: inline-block; padding: 8px 16px; border-radius: 6px; border: none; cursor: pointer; font-size: 14px; font-weight: 500; }
.btn-primary { background: #3498db; color: white; }
.btn-primary:hover { background: #2980b9; }
.btn-danger { background: #e74c3c; color: white; }
.btn-danger:hover { background: #c0392b; }
.btn-success { background: #27ae60; color: white; }
.btn-success:hover { background: #229954; }
.btn-secondary { background: #95a5a6; color: white; }
input, select, textarea { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; margin-top: 4px; }
label { font-size: 13px; color: #666; display: block; margin-top: 12px; }
.error { color: #e74c3c; font-size: 13px; margin-top: 8px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }
th { font-weight: 600; background: #f8f9fa; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 500; }
.badge-blue { background: #ebf5fb; color: #2980b9; }
.badge-green { background: #eafaf1; color: #27ae60; }
.badge-red { background: #fdedec; color: #e74c3c; }
</style>
