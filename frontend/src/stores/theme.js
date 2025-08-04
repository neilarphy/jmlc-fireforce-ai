import { defineStore } from 'pinia'
import { Dark, LocalStorage } from 'quasar'

export const useThemeStore = defineStore('theme', {
    state: () => ({
        darkMode: false
    }),

    getters: {
        isDark: (state) => state.darkMode
    },

    actions: {
        initTheme() {
            const savedTheme = LocalStorage.getItem('darkMode')
            if (savedTheme !== null) {
                this.darkMode = savedTheme
            } else {
                this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches
            }

            this.applyTheme()
        },

        toggleTheme() {
            this.darkMode = !this.darkMode
            this.applyTheme()
            this.saveTheme()
        },

        setTheme(isDark) {
            this.darkMode = isDark
            this.applyTheme()
            this.saveTheme()
        },

        applyTheme() {
            Dark.set(this.darkMode)

            if (this.darkMode) {
                document.body.classList.add('body--dark')
                document.body.classList.remove('body--light')
            } else {
                document.body.classList.add('body--light')
                document.body.classList.remove('body--dark')
            }
        },

        saveTheme() {
            LocalStorage.set('darkMode', this.darkMode)
        }
    }
})