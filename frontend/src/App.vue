<template>
  <div class="min-h-screen flex flex-col">
    <!-- Nav -->
    <nav class="border-b border-gray-800 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <div class="flex items-center gap-8">
          <RouterLink to="/" class="flex items-center gap-2.5 font-semibold text-white">
            <span class="text-brand-500 text-lg">⬡</span>
            Hermes Admin
          </RouterLink>
          <div class="flex items-center gap-1">
            <RouterLink
              v-for="link in links"
              :key="link.to"
              :to="link.to"
              class="px-3 py-1.5 rounded-md text-sm text-gray-400 hover:text-white hover:bg-white/5 transition"
              active-class="text-white bg-white/8"
            >
              {{ link.label }}
            </RouterLink>
          </div>
        </div>
      </div>
    </nav>

    <!-- Page content -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'

const links = [
  { to: '/', label: '用户管理' },
  { to: '/template', label: '默认模板' },
]
</script>
