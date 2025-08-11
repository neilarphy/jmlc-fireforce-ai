import { api } from 'src/boot/axios'

class ApiService {
    static async createPrediction(coordinates) {
        const response = await api.post('/api/v1/predictions/request', {
            latitude: coordinates.latitude,
            longitude: coordinates.longitude,
        })
        return response.data
    }

    static async getPredictionStatus(taskId) {
        const response = await api.get(`/api/v1/predictions/status/${taskId}`)
        return response.data
    }

    static async getPredictionHistory() {
        const response = await api.get('/api/v1/predictions/history')
        return response.data
    }

    static async getPredictionStats() {
        const response = await api.get('/api/v1/predictions/stats')
        return response.data
    }

    static async searchLocation(query) {
        const response = await api.post('/api/v1/predictions/by-location', {
            location_name: query,
        })
        return response.data
    }

    static async getRiskGridData(bounds) {
        const response = await api.get('/api/v1/maps/risk-grid', { params: bounds })
        return response.data
    }

    static async getLocationSuggestions(query) {
        const response = await api.get('/api/v1/search/locations', {
            params: { q: query, limit: 10 },
        })
        return response.data
    }

    static async getWorkersStatus() {
        const response = await api.get('/api/v1/workers/status')
        return response.data
    }

    static async getActiveTasks() {
        const response = await api.get('/api/v1/workers/tasks/active')
        return response.data
    }

    static async getSystemStats() {
        const response = await api.get('/api/v1/health/detailed')
        return response.data
    }

    static async getDashboardStats() {
        const response = await api.get('/api/v1/health/dashboard-stats')
        return response.data
    }

    static async getRosleshozOperative() {
        const response = await api.get('/api/v1/data/rosleshoz/operative')
        return response.data
    }

    static async startHyperparameterOptimization(params) {
        const response = await api.post('/api/v1/optimization/hyperparameters/optimize', params)
        return response.data
    }

    static async getOptimizationStatus(taskId) {
        const response = await api.get(`/api/v1/optimization/hyperparameters/status/${taskId}`)
        return response.data
    }

    static async checkRetrainingTriggers() {
        const response = await api.get('/api/v1/optimization/retraining/triggers')
        return response.data
    }

    static async startRetraining(force = false) {
        const response = await api.post('/api/v1/optimization/retraining/start', { force })
        return response.data
    }

    static async getActiveModel() {
        const response = await api.get('/api/v1/optimization/models/active')
        return response.data
    }
}

export default ApiService