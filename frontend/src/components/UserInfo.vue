<template>
    <div class="user-info">
        <div class="text-weight-bold">{{ userFullName }}</div>
        <div class="text-caption">{{ userEmail }}</div>
    </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from 'src/stores/auth'

const authStore = useAuthStore()

const userFullName = computed(() => authStore.user?.full_name || authStore.user?.username || 'Пользователь')
const userEmail = computed(() => authStore.user?.email || '')
</script>

<style lang="scss" scoped>
.user-info {
    padding: 8px 16px;
}
</style>