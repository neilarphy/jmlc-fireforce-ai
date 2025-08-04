import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from 'src/boot/axios'

export const useAuthStore = defineStore('auth', () => {
    const token = ref('')
    const user = ref(null)
    const loading = ref(false)
    const error = ref(null)

    function loadFromStorage() {
        try {
            const storedToken = localStorage.getItem('token')
            const storedUser = localStorage.getItem('user')

            if (storedToken) {
                token.value = storedToken
            }

            if (storedUser && storedUser !== 'null') {
                user.value = JSON.parse(storedUser)
            }

            console.log('Loaded from storage:', {
                hasToken: !!token.value,
                hasUser: !!user.value,
                user: user.value
            })
        } catch (error) {
            console.error('Error loading from localStorage:', error)
            localStorage.removeItem('token')
            localStorage.removeItem('user')
        }
    }

    const isAuthenticated = computed(() => !!token.value)
    const isAdmin = computed(() => user.value?.role === 'admin')
    const userFullName = computed(() => user.value ? (user.value.full_name || user.value.username) : '')

    async function login(email, password) {
        loading.value = true
        error.value = null

        try {
            const response = await api.post('/api/auth/login', {
                email,
                password
            })

            token.value = response.data.access_token
            user.value = response.data.user

            localStorage.setItem('token', token.value)
            localStorage.setItem('user', JSON.stringify(user.value))

            api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`

            console.log('Authentication state updated, isAuthenticated:', !!token.value)

            return response.data
        } catch (err) {
            error.value = err.response?.data?.message || 'Ошибка входа'
            throw error.value
        } finally {
            loading.value = false
        }
    }

    async function register(userData) {
        loading.value = true
        error.value = null

        try {
            const response = await api.post('/api/auth/register', userData)

            return response.data
        } catch (err) {
            error.value = err.response?.data?.message || 'Ошибка регистрации'
            throw error.value
        } finally {
            loading.value = false
        }
    }

    function logout() {
        token.value = ''
        user.value = null

        localStorage.removeItem('token')
        localStorage.removeItem('user')

        delete api.defaults.headers.common['Authorization']
    }

    function init() {
        console.log('Initializing auth store...')

        loadFromStorage()

        console.log('Auth store initialized:', {
            hasToken: !!token.value,
            hasUser: !!user.value,
            isAuthenticated: !!token.value
        })

        if (token.value) {
            console.log('Setting Authorization header with token')
            api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
        }
    }

    init()

    return {
        token,
        user,
        loading,
        error,

        isAuthenticated,
        isAdmin,
        userFullName,

        login,
        register,
        logout
    }
})