<template>
  <div class="card flex flex-col gap-4">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <p class="font-semibold text-white">{{ user.display_name || user.username }}</p>
        <p class="text-xs text-gray-500 mt-0.5">@{{ user.username }}</p>
        <p v-if="user.email" class="text-xs text-gray-500">{{ user.email }}</p>
      </div>
      <span :class="badgeClass">
        <span class="w-1.5 h-1.5 rounded-full" :class="dotClass" />
        {{ statusLabel }}
      </span>
    </div>

    <!-- Port info -->
    <div class="flex items-center gap-2 text-xs text-gray-500">
      <span class="font-mono bg-gray-800 px-2 py-0.5 rounded">:{{ user.assigned_port }}</span>
      <a
        v-if="status === 'running'"
        :href="`http://localhost:${user.assigned_port}`"
        target="_blank"
        rel="noreferrer"
        class="text-brand-500 hover:underline"
      >
        打开 Dashboard →
      </a>
    </div>

    <!-- Actions -->
    <div class="flex gap-2 flex-wrap">
      <button
        v-if="status !== 'running'"
        class="btn-primary"
        :disabled="loading"
        @click="start"
      >
        {{ loading ? '启动中...' : '▶ 启动' }}
      </button>
      <button
        v-else
        class="btn-ghost"
        :disabled="loading"
        @click="stop"
      >
        ⏹ 停止
      </button>

      <RouterLink :to="`/users/${user.id}/config`" class="btn-ghost">
        ⚙ 配置
      </RouterLink>

      <button class="btn-ghost text-xs" @click="showLogs = !showLogs">
        {{ showLogs ? '收起日志' : '日志' }}
      </button>

      <button class="btn-ghost text-xs text-red-400 hover:text-red-300 ml-auto" @click="$emit('delete', user.id)">
        删除
      </button>
    </div>

    <!-- Logs panel -->
    <div v-if="showLogs" class="bg-gray-950 rounded-lg p-3 max-h-48 overflow-y-auto font-mono text-xs text-gray-400 whitespace-pre-wrap">
      <div v-if="logsLoading" class="text-gray-600">加载中...</div>
      <div v-else-if="logs">{{ logs }}</div>
      <div v-else class="text-gray-600">暂无日志</div>
    </div>

    <p v-if="err" class="text-xs text-red-400">{{ err }}</p>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '../api/index.js'

const props = defineProps({
  user: { type: Object, required: true },
})
const emit = defineEmits(['delete', 'statusChange'])

const status = ref(props.user.container_status || 'stopped')
const loading = ref(false)
const err = ref('')
const showLogs = ref(false)
const logs = ref('')
const logsLoading = ref(false)

watch(() => props.user.container_status, (v) => { status.value = v || 'stopped' })

watch(showLogs, async (v) => {
  if (!v) return
  logsLoading.value = true
  try {
    const res = await api.getLogs(props.user.id)
    logs.value = res.logs || ''
  } catch {
    logs.value = '获取日志失败'
  } finally {
    logsLoading.value = false
  }
})

const badgeClass = computed(() => ({
  running: 'badge-running',
  partial: 'badge-partial',
  stopped: 'badge-stopped',
  not_found: 'badge-stopped',
  docker_unavailable: 'badge-partial',
}[status.value] || 'badge-stopped'))

const dotClass = computed(() => ({
  running: 'bg-emerald-400 animate-pulse',
  partial: 'bg-amber-400',
  stopped: 'bg-gray-500',
  not_found: 'bg-gray-500',
  docker_unavailable: 'bg-amber-400',
}[status.value] || 'bg-gray-500'))

const statusLabel = computed(() => ({
  running: '运行中',
  partial: '部分运行',
  stopped: '已停止',
  not_found: '未创建',
  docker_unavailable: 'Docker 未安装',
}[status.value] || status.value))

async function start() {
  err.value = ''
  loading.value = true
  try {
    await api.startContainer(props.user.id)
    // Poll until running
    await pollStatus('running')
  } catch (e) {
    err.value = e.message
  } finally {
    loading.value = false
  }
}

async function stop() {
  err.value = ''
  loading.value = true
  try {
    await api.stopContainer(props.user.id)
    status.value = 'stopped'
    emit('statusChange', props.user.id, 'stopped')
  } catch (e) {
    err.value = e.message
  } finally {
    loading.value = false
  }
}

async function pollStatus(target, maxRetries = 20) {
  for (let i = 0; i < maxRetries; i++) {
    await new Promise((r) => setTimeout(r, 1500))
    try {
      const res = await api.getStatus(props.user.id)
      status.value = res.status
      emit('statusChange', props.user.id, res.status)
      if (res.status === target) return
    } catch {
      // ignore transient errors
    }
  }
}
</script>
