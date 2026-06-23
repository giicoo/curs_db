<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const router = useRouter()

const role = ref('customer')
const form = ref({
  login: '', password: '', email: '',
  last_name: '', first_name: '', phone: '', delivery_address: '',
  seller_name: '', description: '',
})
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const payload = { login: form.value.login, password: form.value.password, email: form.value.email, role: role.value }
    if (role.value === 'customer') {
      Object.assign(payload, {
        last_name: form.value.last_name,
        first_name: form.value.first_name,
        phone: form.value.phone || undefined,
        delivery_address: form.value.delivery_address || undefined,
      })
    } else {
      Object.assign(payload, {
        seller_name: form.value.seller_name,
        description: form.value.description || undefined,
      })
    }
    await auth.register(payload)
    router.push('/catalog')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="max-width:460px;margin:40px auto">
    <div class="card">
      <h2 style="margin-bottom:20px">Регистрация</h2>
      <form @submit.prevent="submit">
        <label>Роль</label>
        <select v-model="role">
          <option value="customer">Покупатель</option>
          <option value="seller">Продавец</option>
        </select>

        <label>Логин</label>
        <input v-model="form.login" required />
        <label>Email</label>
        <input v-model="form.email" type="email" required />
        <label>Пароль</label>
        <input v-model="form.password" type="password" required />

        <template v-if="role === 'customer'">
          <label>Фамилия</label>
          <input v-model="form.last_name" required />
          <label>Имя</label>
          <input v-model="form.first_name" required />
          <label>Телефон</label>
          <input v-model="form.phone" />
          <label>Адрес доставки</label>
          <input v-model="form.delivery_address" />
        </template>

        <template v-else>
          <label>Название магазина</label>
          <input v-model="form.seller_name" required />
          <label>Описание</label>
          <textarea v-model="form.description" rows="3"></textarea>
        </template>

        <div class="error" v-if="error">{{ error }}</div>
        <button class="btn btn-primary" style="margin-top:16px;width:100%" :disabled="loading">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
      </form>
      <p style="margin-top:12px;font-size:13px;text-align:center">
        Уже есть аккаунт? <router-link to="/login">Войти</router-link>
      </p>
    </div>
  </div>
</template>
