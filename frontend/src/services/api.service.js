import { api } from 'src/boot/axios'

export const ApiService = {
    
    getPredictions(params = {}) {
        return api.get('/api/predictions', { params })
    },

    getPredictionByCoordinates(lat, lng) {
        return api.get(`/api/predictions/${lat}/${lng}`)
    },

    createPrediction(data) {
        return api.post('/api/predict', data)
    },

    getNotifications(params = {}) {
        return api.get('/api/notifications', { params })
    },

    markNotificationAsRead(id) {
        return api.post(`/api/notifications/${id}/read`)
    },

    subscribeToNotifications(preferences) {
        return api.post('/api/notifications/subscribe', { preferences })
    },

    unsubscribeFromNotifications() {
        return api.post('/api/notifications/unsubscribe')
    },

    getProfile() {
        return api.get('/api/profile')
    },

    updateProfile(data) {
        return api.put('/api/profile', data)
    },

    changePassword(data) {
        return api.put('/api/profile/password', data)
    },

    getFireHistory(params = {}) {
        return api.get('/api/history', { params })
    },

    getAnalytics(params = {}) {
        return api.get('/api/analytics', { params })
    },

    getTeams(params = {}) {
        return api.get('/api/teams', { params })
    },

    getHealth() {
        return api.get('/api/health')
    },

    getDetailedHealth() {
        return api.get('/api/health/detailed')
    }
}