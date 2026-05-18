<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" @click.self="$emit('close')">
      <div class="card w-full max-w-md mx-4 shadow-2xl">
        <h2 class="text-lg font-semibold mb-5">新建用户</h2>

        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label class="label">用户名 <span class="text-red-400">*</span></label>
            <input v-model="form.username" class="input" placeholder="alice" required pattern="[a-z0-9_-]+" />
            <p class="mt-1 text-xs text-gray-500">只允许小写字母、数字、- 和 _</p>
          </div>
          <div>
            <label class="label">显示名称</label>
            <input v-model="form.display_name" class="input" placeholder="Alice" />
          </div>
          <div>
            <label class="label">邮箱</label>
            <input v-model="form.email" type="email" class="input" placeholder="alice@example.com" />
          </div>

          <p v-if="error" class="text-sm text-red-400">{{ error }}</p>

          <div class="flex gap-3 pt-2">
            <button type="button" class="btn-ghost flex-1" @click="$emit('close')">取消</button>
            <button type="submit" class="btn-primary flex-1" :disabled="loading">
              {{ loading ? '创建中...' : '创建用户' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { api } from '../api/index.js'

const emit = defineEmits(['close', 'created'])

const form = reactive({ username: '', display_name: '', email: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const user = await api.createUser(form)
    emit('created', user)
    emit('close')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
