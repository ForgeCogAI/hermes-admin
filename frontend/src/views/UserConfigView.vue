<template>
  <div class="max-w-2xl">
    <!-- Back -->
    <RouterLink to="/" class="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-white mb-6 transition">
      ← 返回用户列表
    </RouterLink>

    <div class="mb-8">
      <h1 class="text-2xl font-bold text-white">用户配置</h1>
      <p class="text-sm text-gray-500 mt-1">
        空值字段将继承管理员模板的设定。非空值将覆盖模板。
      </p>
    </div>

    <div v-if="loading" class="card text-gray-500 text-sm">加载中...</div>
    <div v-else-if="loadErr" class="card text-red-400 text-sm">{{ loadErr }}</div>

    <template v-else>
      <!-- Merged preview -->
      <div class="card mb-4 bg-gray-800/50">
        <p class="text-xs text-gray-500 font-medium mb-2">当前生效配置（模板 + 用户覆盖合并）</p>
        <div class="text-xs text-gray-300 space-y-1 font-mono">
          <div><span class="text-gray-600">model:</span> {{ merged.model || '—' }}</div>
          <div><span class="text-gray-600">base_url:</span> {{ merged.base_url || '官方默认' }}</div>
          <div><span class="text-gray-600">reasoning_effort:</span> {{ merged.reasoning_effort || '—' }}</div>
          <div><span class="text-gray-600">max_turns:</span> {{ merged.max_turns ?? '—' }}</div>
          <div><span class="text-gray-600">api_key:</span> {{ merged.api_key ? '••••••••' : '未设置' }}</div>
        </div>
      </div>

      <div class="card">
        <p class="text-xs text-gray-500 mb-4">以下为该用户的个人覆盖值（留空 = 继承模板）</p>
        <ConfigForm v-model="userConfig">
          <template #default="{ config: current }">
            <div class="flex items-center gap-3 pt-2">
              <button class="btn-primary" :disabled="saving" @click="save(current)">
                {{ saving ? '保存中...' : '保存配置' }}
              </button>
              <button class="btn-ghost" :disabled="restarting" @click="restart">
                {{ restarting ? '重启中...' : '保存并重启容器' }}
              </button>
              <p v-if="saved" class="text-sm text-emerald-400">✓ 已保存</p>
              <p v-if="err" class="text-sm text-red-400">{{ err }}</p>
            </div>
          </template>
        </ConfigForm>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { api } from '../api/index.js'
import ConfigForm from '../components/ConfigForm.vue'

const route = useRoute()
const userId = Number(route.params.id)

const loading = ref(true)
const loadErr = ref('')
const saving = ref(false)
const restarting = ref(false)
const saved = ref(false)
const err = ref('')

const templateConfig = ref({})
const userConfig = ref({})

const merged = computed(() => {
  const base = { ...templateConfig.value }
  for (const [k, v] of Object.entries(userConfig.value)) {
    if (v !== null && v !== undefined && v !== '') base[k] = v
  }
  return base
})

onMounted(async () => {
  try {
    const [tmpl, userCfg] = await Promise.all([
      api.getTemplate(),
      api.getUserConfig(userId),
    ])
    templateConfig.value = JSON.parse(tmpl.config_json || '{}')
    userConfig.value = JSON.parse(userCfg.config_json || '{}')
  } catch (e) {
    loadErr.value = e.message
  } finally {
    loading.value = false
  }
})

async function save(current) {
  saving.value = true
  saved.value = false
  err.value = ''
  try {
    await api.updateUserConfig(userId, JSON.stringify(current))
    userConfig.value = current
    saved.value = true
    setTimeout(() => { saved.value = false }, 2000)
  } catch (e) {
    err.value = e.message
  } finally {
    saving.value = false
  }
}

async function restart() {
  restarting.value = true
  err.value = ''
  try {
    await api.updateUserConfig(userId, JSON.stringify(userConfig.value))
    await api.restartContainer(userId)
    saved.value = true
    setTimeout(() => { saved.value = false }, 2000)
  } catch (e) {
    err.value = e.message
  } finally {
    restarting.value = false
  }
}
</script>
