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
    error.value = e.response?.data?.detail || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div style="max-width:400px;margin:60px auto">
    <div class="card">
      <h2 style="margin-bottom:20px">Вход в систему</h2>
      <form @submit.prevent="submit">
        <label>Логин</label>
        <input v-model="form.login" required />
        <label>Пароль</label>
        <input v-model="form.password" type="password" required />
        <div class="error" v-if="error">{{ error }}</div>
        <button class="btn btn-primary" style="margin-top:16px;width:100%" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>
      <p style="margin-top:16px;font-size:13px;text-align:center">
        Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link>
      </p>
      <p style="margin-top:8px;font-size:12px;color:#999;text-align:center">
        Тест: user1/Test1234! (покупатель), user301/Test1234! (продавец)
      </p>
    </div>
  </div>
</template>
