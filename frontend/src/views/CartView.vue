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
  if (cart.items.length === 0) { error.value = 'Корзина пуста'; return }
  error.value = ''
  submitting.value = true
  try {
    const { data } = await api.post('/orders', {
      delivery_address: address.value,
      items: cart.items.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
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
    <h1 style="margin-bottom:20px">Корзина</h1>

    <div v-if="cart.items.length === 0" style="text-align:center;padding:60px;color:#999">
      Корзина пуста. <router-link to="/catalog">Перейти в каталог</router-link>
    </div>

    <div v-else>
      <div class="card" style="margin-bottom:16px">
        <table>
          <thead>
            <tr><th>Товар</th><th>Цена</th><th>Количество</th><th>Сумма</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-for="item in cart.items" :key="item.product_id">
              <td>
                <router-link :to="`/product/${item.product_id}`">{{ item.name }}</router-link>
                <div style="font-size:12px;color:#888">{{ item.seller_name }}</div>
              </td>
              <td>{{ item.price.toFixed(2) }} ₽</td>
              <td>
                <div style="display:flex;align-items:center;gap:8px">
                  <button class="btn btn-secondary" style="padding:4px 10px" @click="cart.updateQty(item.product_id, item.quantity - 1)">−</button>
                  <span>{{ item.quantity }}</span>
                  <button class="btn btn-secondary" style="padding:4px 10px" @click="cart.updateQty(item.product_id, item.quantity + 1)">+</button>
                </div>
              </td>
              <td>{{ (item.price * item.quantity).toFixed(2) }} ₽</td>
              <td><button class="btn btn-danger" style="padding:4px 10px" @click="cart.remove(item.product_id)">✕</button></td>
            </tr>
          </tbody>
        </table>
        <div style="text-align:right;margin-top:12px;font-size:18px;font-weight:bold">
          Итого: {{ cart.total.toFixed(2) }} ₽
        </div>
      </div>

      <div class="card">
        <h3 style="margin-bottom:12px">Оформление заказа</h3>
        <label>Адрес доставки</label>
        <input v-model="address" placeholder="Введите адрес доставки" />
        <div class="error" v-if="error">{{ error }}</div>
        <button class="btn btn-success" style="margin-top:16px" @click="placeOrder" :disabled="submitting">
          {{ submitting ? 'Оформление...' : 'Оформить заказ' }}
        </button>
      </div>
    </div>
  </div>
</template>
