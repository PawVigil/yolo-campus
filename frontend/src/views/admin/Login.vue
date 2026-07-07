<template>
  <div class="login-page">
    <div class="login-card-wrapper">
      <div class="login-header">
        <div class="login-logo">🐾</div>
        <h1>PawVigil</h1>
        <p>校园流浪动物观测关爱系统 · 管理端</p>
      </div>
      <n-card :bordered="false" class="login-card">
        <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
          <n-form-item label="用户名" path="username">
            <n-input v-model:value="form.username" placeholder="请输入用户名" size="large" />
          </n-form-item>
          <n-form-item label="密码" path="password">
            <n-input v-model:value="form.password" type="password" placeholder="请输入密码" size="large" @keyup.enter="doLogin" />
          </n-form-item>
          <n-button type="primary" block size="large" :loading="loading" @click="doLogin">
            {{ loading ? '登录中...' : '🔐 登录' }}
          </n-button>
        </n-form>
        <n-divider />
        <p class="login-hint">💡 演示账号：admin / admin123</p>
        <n-button text @click="$router.push('/')" class="back-link">← 返回实时大屏</n-button>
      </n-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { login } from '@/api/admin.js'
import { authStore } from '@/stores/auth.js'

const router = useRouter()
const message = useMessage()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function doLogin() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    const res = await login(form.username, form.password)
    authStore.login(res.token, res.username)
    message.success(`欢迎回来，${res.username}！`)
    router.push('/admin/dashboard')
  } catch (e) {
    const detail = e?.response?.data?.detail || '登录失败'
    message.error(detail)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card-wrapper {
  width: 100%;
  max-width: 420px;
  padding: 20px;
}
.login-header {
  text-align: center;
  color: #fff;
  margin-bottom: 24px;
}
.login-logo {
  font-size: 56px;
}
.login-header h1 {
  font-size: 28px;
  margin: 8px 0 4px;
}
.login-header p {
  font-size: 14px;
  opacity: 0.8;
}
.login-card {
  border-radius: 12px;
}
.login-hint {
  text-align: center;
  font-size: 13px;
  color: #909399;
}
.back-link {
  display: block;
  margin: 8px auto 0;
}
</style>
