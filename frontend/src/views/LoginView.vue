<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ login: '', password: '' })
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.value.login, form.value.password)
    router.push('/catalog')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Неверный логин или пароль'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <div class="auth-brand">Маркетплейс</div>
      <h2 class="auth-title">Войдите в аккаунт</h2>

      <form @submit.prevent="submit" class="auth-form">
        <div class="field">
          <label for="login">Логин</label>
          <input id="login" v-model="form.login" placeholder="user1" autocomplete="username" required />
        </div>
        <div class="field">
          <label for="password">Пароль</label>
          <input id="password" v-model="form.password" type="password" placeholder="••••••••" autocomplete="current-password" required />
        </div>

        <div v-if="error" class="error">{{ error }}</div>

        <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>

      <p class="auth-foot">
        Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link>
      </p>
      <p class="auth-hint">
        Тест: <code>user1 / Test1234!</code> (покупатель) &nbsp;·&nbsp; <code>user301 / Test1234!</code> (продавец)
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-wrap {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
}
.auth-card {
  width: 100%;
  max-width: 380px;
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
  margin-bottom: 20px;
}
.auth-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 24px;
}
.auth-form { display: flex; flex-direction: column; gap: 0; }
.field { margin-bottom: 14px; }
.field label { margin-top: 0; margin-bottom: 5px; }
.btn-full { width: 100%; margin-top: 6px; padding: 10px; font-size: 14px; }
.auth-foot {
  text-align: center;
  font-size: 13px;
  color: #64748b;
  margin-top: 20px;
}
.auth-hint {
  text-align: center;
  font-size: 11.5px;
  color: #b0bac7;
  margin-top: 14px;
  line-height: 1.6;
}
code {
  background: #f1f5f9;
  padding: 1px 5px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Fira Mono', monospace;
  color: #475569;
}
</style>
