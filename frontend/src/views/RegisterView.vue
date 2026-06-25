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
    const payload = {
      login: form.value.login,
      password: form.value.password,
      email: form.value.email,
      role: role.value,
    }
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
  <div class="auth-wrap">
    <div class="auth-card">
      <div class="auth-brand">Маркетплейс</div>
      <h2 class="auth-title">Создать аккаунт</h2>

      <!-- Role toggle -->
      <div class="role-toggle">
        <button
          type="button"
          :class="['role-btn', role === 'customer' && 'active']"
          @click="role = 'customer'">
          Покупатель
        </button>
        <button
          type="button"
          :class="['role-btn', role === 'seller' && 'active']"
          @click="role = 'seller'">
          Продавец
        </button>
      </div>

      <form @submit.prevent="submit">
        <div class="field-row">
          <div class="field">
            <label>Логин</label>
            <input v-model="form.login" placeholder="mylogin" autocomplete="username" required />
          </div>
          <div class="field">
            <label>Email</label>
            <input v-model="form.email" type="email" placeholder="user@example.com" required />
          </div>
        </div>
        <div class="field">
          <label>Пароль</label>
          <input v-model="form.password" type="password" placeholder="Минимум 8 символов" autocomplete="new-password" required />
        </div>

        <div class="section-divider">
          <span>{{ role === 'customer' ? 'Данные покупателя' : 'Данные продавца' }}</span>
        </div>

        <template v-if="role === 'customer'">
          <div class="field-row">
            <div class="field">
              <label>Фамилия</label>
              <input v-model="form.last_name" placeholder="Иванов" required />
            </div>
            <div class="field">
              <label>Имя</label>
              <input v-model="form.first_name" placeholder="Иван" required />
            </div>
          </div>
          <div class="field">
            <label>Телефон <span class="opt">(необязательно)</span></label>
            <input v-model="form.phone" placeholder="+375291234567" />
          </div>
          <div class="field">
            <label>Адрес доставки <span class="opt">(необязательно)</span></label>
            <input v-model="form.delivery_address" placeholder="Минск, ул. Ленина, д. 1" />
          </div>
        </template>

        <template v-else>
          <div class="field">
            <label>Название магазина</label>
            <input v-model="form.seller_name" placeholder="Мой магазин" required />
          </div>
          <div class="field">
            <label>Описание <span class="opt">(необязательно)</span></label>
            <textarea v-model="form.description" placeholder="Расскажите о вашем магазине..." rows="3"></textarea>
          </div>
        </template>

        <div v-if="error" class="error">{{ error }}</div>

        <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
      </form>

      <p class="auth-foot">
        Уже есть аккаунт? <router-link to="/login">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-wrap {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 32px 16px;
}
.auth-card {
  width: 100%;
  max-width: 480px;
  background: #fff;
  border-radius: 14px;
  padding: 36px 32px;
  border: 1px solid #e9edf2;
  box-shadow: 0 4px 20px rgba(0,0,0,.06);
}
.auth-brand {
  font-size: 15px;
  font-weight: 700;
  color: #4f46e5;
  letter-spacing: -.02em;
  margin-bottom: 18px;
}
.auth-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 22px;
}
.role-toggle {
  display: flex;
  background: #f1f5f9;
  border-radius: 9px;
  padding: 3px;
  margin-bottom: 22px;
}
.role-btn {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 7px;
  font-size: 13.5px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  background: transparent;
  color: #64748b;
  transition: background .14s, color .14s, box-shadow .14s;
}
.role-btn.active {
  background: #fff;
  color: #4f46e5;
  box-shadow: 0 1px 4px rgba(0,0,0,.1);
}
.field { margin-bottom: 12px; }
.field label { margin-top: 0; margin-bottom: 5px; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.section-divider {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 18px 0 14px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: .06em;
}
.section-divider::before,
.section-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e9edf2;
}
.opt { color: #94a3b8; font-weight: 400; }
.btn-full { width: 100%; margin-top: 8px; padding: 10px; font-size: 14px; }
.auth-foot {
  text-align: center;
  font-size: 13px;
  color: #64748b;
  margin-top: 20px;
}
</style>
