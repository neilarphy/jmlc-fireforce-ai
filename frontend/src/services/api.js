
import { api } from 'src/boot/axios'

export class ApiService {
    
    static async createPrediction(coordinates) {
        try {
            const response = await api.post('/api/v1/predictions/request', {
                latitude: coordinates.latitude,
                longitude: coordinates.longitude
            })
            return response.data
        } catch (error) {
            console.error('Error creating prediction:', error)
            throw error
        }
    }

    static async getPredictionStatus(taskId) {
        try {
            const response = await api.get(`/api/v1/predictions/status/${taskId}`)
            return response.data
        } catch (error) {
            console.error('Error getting prediction status:', error)
            throw error
        }
    }

    static async getPredictionHistory() {
        try {
            const response = await api.get('/api/v1/predictions/history')
            return response.data
        } catch (error) {
            console.error('Error getting prediction history:', error)
            throw error
        }
    }

    static async getPredictionStats() {
        try {
            const response = await api.get('/api/v1/predictions/stats')
            return response.data
        } catch (error) {
            console.error('Error getting prediction stats:', error)
            throw error
        }
    }

    static async searchLocation(query) {
        try {
            const response = await api.post('/api/v1/predictions/by-location', {
                location_name: query
            })
            return response.data
        } catch (error) {
            console.error('Error searching location:', error)
            throw error
        }
    }

    static async getRiskGridData(bounds) {
        try {
            const response = await api.get('/api/v1/maps/risk-grid', {
                params: bounds
            })
            return response.data
        } catch (error) {
            console.error('Error getting risk grid data:', error)
            throw error
        }
    }

    static async getLocationSuggestions(query) {
        try {
            const response = await api.get('/api/v1/search/locations', {
                params: { q: query, limit: 10 }
            })
            return response.data
        } catch (error) {
            console.error('Error getting location suggestions:', error)
            throw error
        }
    }

    static async getWorkersStatus() {
        try {
            const response = await api.get('/api/v1/workers/status')
            return response.data
        } catch (error) {
            console.error('Error getting workers status:', error)
            throw error
        }
    }

    static async getActiveTasks() {
        try {
            const response = await api.get('/api/v1/workers/tasks/active')
            return response.data
        } catch (error) {
            console.error('Error getting active tasks:', error)
            throw error
        }
    }

    static async getSystemStats() {
        try {
            const response = await api.get('/api/v1/health/detailed')
            return response.data
        } catch (error) {
            console.error('Error getting system stats:', error)
            throw error
        }
    }

    static async startHyperparameterOptimization(params) {
        try {
            const response = await api.post('/api/v1/optimization/hyperparameters/optimize', params)
            return response.data
        } catch (error) {
            console.error('Error starting hyperparameter optimization:', error)
            throw error
        }
    }

    static async getOptimizationStatus(taskId) {
        try {
            const response = await api.get(`/api/v1/optimization/hyperparameters/status/${taskId}`)
            return response.data
        } catch (error) {
            console.error('Error getting optimization status:', error)
            throw error
        }
    }

    static async checkRetrainingTriggers() {
        try {
            const response = await api.get('/api/v1/optimization/retraining/triggers')
            return response.data
        } catch (error) {
            console.error('Error checking retraining triggers:', error)
            throw error
        }
    }

    static async startRetraining(force = false) {
        try {
            const response = await api.post('/api/v1/optimization/retraining/start', { force })
            return response.data
        } catch (error) {
            console.error('Error starting retraining:', error)
            throw error
        }
    }

    static async getActiveModel() {
        try {
            const response = await api.get('/api/v1/optimization/models/active')
            return response.data
        } catch (error) {
            console.error('Error getting active model:', error)
            throw error
        }
    }
}

export default ApiService