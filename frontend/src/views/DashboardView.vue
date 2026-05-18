<template>
  <div>
    <!-- Page header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-bold text-white">用户管理</h1>
        <p class="text-sm text-gray-500 mt-1">管理所有 Hermes 用户实例</p>
      </div>
      <button class="btn-primary" @click="showCreate = true">+ 新建用户</button>
    </div>

    <!-- Image missing warning banner -->
    <div v-if="imageHint" class="mb-6 rounded-xl border border-amber-700/50 bg-amber-950/40 p-4">
      <p class="text-sm font-medium text-amber-400 mb-2">⚠ Docker 镜像未就绪</p>
      <pre class="text-xs text-amber-300/80 whitespace-pre-wrap font-mono">{{ imageHint }}</pre>
    </div>

    <!-- Stats bar -->
    <div class="grid grid-cols-3 gap-4 mb-8">
      <div class="card text-center">
        <p class="text-3xl font-bold text-white">{{ users.length }}</p>
        <p class="text-xs text-gray-500 mt-1">用户总数</p>
      </div>
      <div class="card text-center">
        <p class="text-3xl font-bold text-emerald-400">{{ runningCount }}</p>
        <p class="text-xs text-gray-500 mt-1">运行中</p>
      </div>
      <div class="card text-center">
        <p class="text-3xl font-bold text-gray-400">{{ stoppedCount }}</p>
        <p class="text-xs text-gray-500 mt-1">已停止</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center text-gray-500 py-20">加载中...</div>

    <!-- Error -->
    <div v-else-if="error" class="card text-red-400 text-sm">{{ error }}</div>

    <!-- Empty -->
    <div v-else-if="users.length === 0" class="card text-center py-16 text-gray-500">
      <p class="text-4xl mb-3">⬡</p>
      <p class="font-medium">还没有用户</p>
      <p class="text-sm mt-1">点击「新建用户」开始</p>
    </div>

    <!-- User grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <UserCard
        v-for="user in users"
        :key="user.id"
        :user="user"
        @delete="confirmDelete"
        @statusChange="onStatusChange"
      />
    </div>

    <!-- Modals -->
    <CreateUserModal v-if="showCreate" @close="showCreate = false" @created="onCreated" />

    <!-- Delete confirm -->
    <Teleport v-if="deleteId !== null" to="body">
      <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div class="card max-w-sm mx-4 shadow-2xl">
          <p class="font-semibold text-white mb-2">确认删除？</p>
          <p class="text-sm text-gray-400 mb-5">这会停止并移除该用户实例（不删除磁盘数据）。</p>
          <div class="flex gap-3">
            <button class="btn-ghost flex-1" @click="deleteId = null">取消</button>
            <button class="btn-danger flex-1" @click="doDelete">确认删除</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api/index.js'
import CreateUserModal from '../components/CreateUserModal.vue'
import UserCard from '../components/UserCard.vue'

const users = ref([])
const loading = ref(false)
const error = ref('')
const showCreate = ref(false)
const deleteId = ref(null)
const imageHint = ref('')

const runningCount = computed(() => users.value.filter((u) => u.container_status === 'running').length)
const stoppedCount = computed(() => users.value.filter((u) => u.container_status !== 'running').length)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [usersData, sysStatus] = await Promise.all([
      api.listUsers(),
      api.systemStatus(),
    ])
    users.value = usersData
    imageHint.value = sysStatus.image_hint || ''
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function onCreated(user) {
  users.value.push(user)
}

function onStatusChange(userId, newStatus) {
  const u = users.value.find((x) => x.id === userId)
  if (u) u.container_status = newStatus
}

function confirmDelete(id) {
  deleteId.value = id
}

async function doDelete() {
  try {
    await api.deleteUser(deleteId.value)
    users.value = users.value.filter((u) => u.id !== deleteId.value)
  } catch (e) {
    error.value = e.message
  } finally {
    deleteId.value = null
  }
}

onMounted(load)
</script>
