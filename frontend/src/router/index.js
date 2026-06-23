import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const routes = [
  { path: '/', redirect: '/catalog' },
  { path: '/login', component: () => import('../views/LoginView.vue') },
  { path: '/register', component: () => import('../views/RegisterView.vue') },
  { path: '/catalog', component: () => import('../views/CatalogView.vue') },
  { path: '/product/:id', component: () => import('../views/ProductView.vue') },
  {
    path: '/cart',
    component: () => import('../views/CartView.vue'),
    meta: { requiresAuth: true, role: 'customer' },
  },
  {
    path: '/orders',
    component: () => import('../views/OrdersView.vue'),
    meta: { requiresAuth: true, role: 'customer' },
  },
  {
    path: '/seller/products',
    component: () => import('../views/seller/ProductsView.vue'),
    meta: { requiresAuth: true, role: 'seller' },
  },
  {
    path: '/seller/orders',
    component: () => import('../views/seller/SellerOrdersView.vue'),
    meta: { requiresAuth: true, role: 'seller' },
  },
  {
    path: '/seller/low-stock',
    component: () => import('../views/seller/LowStockView.vue'),
    meta: { requiresAuth: true, role: 'seller' },
  },
  {
    path: '/reports',
    component: () => import('../views/ReportsView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (auth.isAuthenticated && !auth.user) {
    await auth.fetchMe()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/login'
  }

  if (to.meta.role && auth.role !== to.meta.role) {
    return '/catalog'
  }
})

export default router
