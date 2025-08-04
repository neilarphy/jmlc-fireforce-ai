import { useAuthStore } from 'src/stores/auth'

export function authGuard(to, from, next) {
    const authStore = useAuthStore()

    console.log('Auth guard check:', {
        path: to.path,
        fullPath: to.fullPath,
        requiresAuth: to.meta.requiresAuth,
        isAuthenticated: authStore.isAuthenticated,
        token: authStore.token ? 'exists' : 'missing'
    })

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        console.log('Redirecting to login, user not authenticated')
        next({
            path: '/login',
            query: { redirect: to.fullPath }
        })
    } else {
        console.log('Allowing access to protected route')
        next()
    }
}

export function guestGuard(to, from, next) {
    const authStore = useAuthStore()

    console.log('Guest guard check:', {
        path: to.path,
        isAuthenticated: authStore.isAuthenticated,
        redirectQuery: to.query.redirect
    })

    if (authStore.isAuthenticated) {
        const redirectPath = to.query.redirect || '/'
        console.log('Redirecting authenticated user to:', redirectPath)
        next({ path: redirectPath })
    } else {
        console.log('Allowing access to guest page:', to.path)
        next()
    }
}

export function adminGuard(to, from, next) {
    const authStore = useAuthStore()

    if (to.meta.requiresAdmin && (!authStore.isAuthenticated || !authStore.isAdmin)) {
        next({ path: '/' })
    } else {
        next()
    }
}