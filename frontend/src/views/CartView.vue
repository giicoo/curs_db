<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart.js'
import { useAuthStore } from '../stores/auth.js'
import api from '../api/index.js'

const cart = useCartStore()
const auth = useAuthStore()
const router = useRouter()

const address = ref(auth.user?.profile?.delivery_address || '')
const error = ref('')
const submitting = ref(false)

async function placeOrder() {
  if (!address.value.trim()) { error.value = 'Укажите адрес доставки'; return }
  if (!cart.items.length) { error.value = 'Корзина пуста'; return }
  error.value = ''
  submitting.value = true
  try {
    await api.post('/orders', {
      delivery_address: address.value,
      items: cart.items.map(i => ({ product_id: i.product_id, quantity: i.quantity })),
    })
    cart.clear()
    router.push('/orders')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка оформления заказа'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <div class="page-title">
      <h1>Корзина</h1>
      <span v-if="cart.items.length" class="muted text-sm">{{ cart.count }} товаров</span>
    </div>

    <div v-if="!cart.items.length" class="empty-state card">
      <div style="font-size:36px;margin-bottom:12px;color:#e2e8f0">&#x1F6D2;</div>
      <p>Корзина пуста</p>
      <router-link to="/catalog" style="margin-top:14px;display:inline-block" class="btn btn-primary btn-sm">Перейти в каталог</router-link>
    </div>

    <div v-else class="cart-layout">
      <!-- Cart items -->
      <div class="card cart-items">
        <div v-for="item in cart.items" :key="item.product_id" class="cart-row">
          <div class="cart-item-info">
            <div class="item-thumb">{{ item.name.slice(0,2).toUpperCase() }}</div>
            <div>
              <router-link :to="`/product/${item.product_id}`" class="item-name">{{ item.name }}</router-link>
              <div class="item-seller muted text-sm">{{ item.seller_name }}</div>
            </div>
          </div>
          <div class="cart-item-right">
            <div class="qty-ctrl">
              <button class="qty-btn" @click="cart.updateQty(item.product_id, item.quantity - 1)">−</button>
              <span class="qty-val">{{ item.quantity }}</span>
              <button class="qty-btn" @click="cart.updateQty(item.product_id, item.quantity + 1)">+</button>
            </div>
            <div class="item-price">{{ (item.price * item.quantity).toFixed(2) }} ₽</div>
            <button class="btn btn-ghost btn-icon btn-sm remove-btn" @click="cart.remove(item.product_id)" title="Удалить">✕</button>
          </div>
        </div>
      </div>

      <!-- Order summary -->
      <div class="cart-sidebar">
        <div class="card summary-card">
          <h3 style="margin-bottom:16px">Оформление заказа</h3>

          <div class="summary-lines">
            <div class="summary-line" v-for="item in cart.items" :key="item.product_id">
              <span class="muted text-sm">{{ item.name }} × {{ item.quantity }}</span>
              <span class="text-sm">{{ (item.price * item.quantity).toFixed(2) }} ₽</span>
            </div>
          </div>

          <div class="summary-total">
            <span>Итого</span>
            <span>{{ cart.total.toFixed(2) }} ₽</span>
          </div>

          <label style="margin-top:16px">Адрес доставки</label>
          <textarea v-model="address" rows="2" placeholder="Укажите адрес доставки"></textarea>

          <div v-if="error" class="error">{{ error }}</div>

          <button class="btn btn-success btn-full" style="margin-top:14px" @click="placeOrder" :disabled="submitting">
            {{ submitting ? 'Оформление...' : 'Оформить заказ' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cart-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 18px;
  align-items: start;
}

.cart-items { padding: 0; overflow: hidden; }

.cart-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 20px;
  border-bottom: 1px solid #f1f5f9;
}
.cart-row:last-child { border-bottom: none; }

.cart-item-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}
.item-thumb {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: linear-gradient(135deg, #eef2ff, #e0e7ff);
  color: #a5b4fc;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.item-name {
  font-size: 13.5px;
  font-weight: 500;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
  display: block;
}
.item-name:hover { color: #4f46e5; }

.cart-item-right {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}

.qty-ctrl {
  display: flex;
  align-items: center;
  gap: 0;
  border: 1.5px solid #e2e8f0;
  border-radius: 7px;
  overflow: hidden;
}
.qty-btn {
  width: 30px;
  height: 30px;
  border: none;
  background: #f8fafc;
  color: #475569;
  font-size: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background .12s;
}
.qty-btn:hover { background: #e2e8f0; }
.qty-val {
  min-width: 28px;
  text-align: center;
  font-size: 13.5px;
  font-weight: 600;
  padding: 0 4px;
}

.item-price {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  min-width: 90px;
  text-align: right;
}
.remove-btn { color: #94a3b8; }
.remove-btn:hover { color: #dc2626; border-color: #fecaca; background: #fef2f2; }

/* Summary */
.summary-card { }
.summary-lines { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.summary-line { display: flex; justify-content: space-between; gap: 8px; }
.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  padding-top: 12px;
  border-top: 1px solid #e9edf2;
}
.btn-full { width: 100%; padding: 11px; font-size: 14px; }

@media (max-width: 760px) {
  .cart-layout { grid-template-columns: 1fr; }
}
</style>
