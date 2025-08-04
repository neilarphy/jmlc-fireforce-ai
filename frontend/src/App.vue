<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'
import { useThemeStore } from 'src/stores/theme'
import { initColorScheme } from 'src/utils/colorScheme'

const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

onMounted(() => {
  console.log('App mounted')
  console.log('Current route:', route.path)
  console.log('Auth status:', authStore.isAuthenticated)

  // Инициализируем тему и цветовую схему
  themeStore.initTheme()
  initColorScheme()

  const token = localStorage.getItem('token')
  console.log('Token in localStorage:', token ? 'exists' : 'not found')
})
</script>
