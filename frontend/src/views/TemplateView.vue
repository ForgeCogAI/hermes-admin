<template>
  <div class="max-w-2xl">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-white">默认配置模板</h1>
      <p class="text-sm text-gray-500 mt-1">新用户创建时将使用此模板作为初始配置。用户可在各自页面中覆盖。</p>
    </div>

    <div v-if="loading" class="card text-gray-500 text-sm">加载中...</div>

    <div v-else class="card">
      <ConfigForm v-model="config">
        <template #default="{ config: current }">
          <div class="flex items-center gap-3 pt-2">
            <button class="btn-primary" :disabled="saving" @click="save(current)">
              {{ saving ? '保存中...' : '保存模板' }}
            </button>
            <p v-if="saved" class="text-sm text-emerald-400">✓ 已保存</p>
            <p v-if="err" class="text-sm text-red-400">{{ err }}</p>
          </div>
        </template>
      </ConfigForm>
    </div>

    <div class="mt-6 card bg-amber-950/30 border-amber-900/50">
      <p class="text-xs text-amber-400 font-medium mb-1">注意</p>
      <p class="text-xs text-amber-300/70">
        修改模板不会自动更新已有用户的配置。若需同步，请进入各用户配置页面手动调整，或重启该用户的容器（重启时会重新合并模板+用户覆盖）。
      </p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api/index.js'
import ConfigForm from '../components/ConfigForm.vue'

const loading = ref(true)
const saving = ref(false)
const saved = ref(false)
const err = ref('')
const config = ref({})

onMounted(async () => {
  try {
    const tmpl = await api.getTemplate()
    config.value = JSON.parse(tmpl.config_json || '{}')
  } catch (e) {
    err.value = e.message
  } finally {
    loading.value = false
  }
})

async function save(current) {
  saving.value = true
  saved.value = false
  err.value = ''
  try {
    await api.updateTemplate(JSON.stringify(current))
    saved.value = true
    setTimeout(() => { saved.value = false }, 2000)
  } catch (e) {
    err.value = e.message
  } finally {
    saving.value = false
  }
}
</script>
