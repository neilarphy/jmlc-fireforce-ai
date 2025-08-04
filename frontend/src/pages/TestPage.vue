<template>
    <q-page class="q-pa-md">
        <q-card class="q-pa-lg">
            <div class="text-h4 q-mb-md">Тестовая страница</div>
            <div class="text-subtitle1 q-mb-md">Эта страница не требует авторизации</div>

            <div class="q-mb-md">
                <div><strong>Токен в localStorage:</strong> {{ tokenExists ? 'Есть' : 'Нет' }}</div>
                <div><strong>Пользователь в localStorage:</strong> {{ userExists ? 'Есть' : 'Нет' }}</div>
                <div><strong>Статус аутентификации:</strong> {{ authStatus }}</div>
            </div>

            <div class="q-gutter-md">
                <q-btn color="primary" label="Перейти на логин" to="/login" />
                <q-btn color="secondary" label="Попробовать главную" to="/" />
                <q-btn color="green" label="Очистить localStorage" @click="clearStorage" />
            </div>
        </q-card>
    </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from 'src/stores/auth'

const authStore = useAuthStore()
const tokenExists = ref(false)
const userExists = ref(false)

const authStatus = computed(() => authStore.isAuthenticated ? 'Авторизован' : 'Не авторизован')

function checkStorage() {
    tokenExists.value = !!localStorage.getItem('token')
    userExists.value = !!localStorage.getItem('user')

    console.log('Storage check:', {
        token: localStorage.getItem('token'),
        user: localStorage.getItem('user'),
        authStoreToken: authStore.token,
        authStoreUser: authStore.user,
        isAuthenticated: authStore.isAuthenticated
    })
}

function clearStorage() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    authStore.logout()
    checkStorage()
}

onMounted(() => {
    console.log('TestPage mounted')
    checkStorage()
})
</script>