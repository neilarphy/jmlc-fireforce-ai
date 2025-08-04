<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page class="auth-page">
        <!-- Фоновая анимация -->
        <div class="background-animation">
          <div class="fire-particle" v-for="n in 20" :key="n" :style="getParticleStyle(n)"></div>
        </div>

        <!-- Основной контент -->
        <div class="auth-container">
          <!-- Левая часть - информация о продукте -->
          <div class="info-section">
            <div class="logo-section">
              <div class="fire-icon-container">
                <q-icon name="local_fire_department" size="60px" class="fire-icon" />
              </div>
              <h1 class="logo-text">FireForceAI</h1>
              <p class="tagline">Система предсказания пожаров нового поколения</p>
            </div>

            <div class="features">
              <div class="feature-item" v-for="feature in features" :key="feature.title">
                <q-icon :name="feature.icon" size="24px" color="white" />
                <div>
                  <h3>{{ feature.title }}</h3>
                  <p>{{ feature.description }}</p>
                </div>
              </div>
            </div>

            <div class="stats">
              <div class="stat-item" v-for="stat in stats" :key="stat.label">
                <div class="stat-number">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
          </div>

          <!-- Правая часть - форма аутентификации -->
          <div class="form-section">
            <div class="form-container">
              <div class="form-header">
                <h2>{{ isLogin ? 'Добро пожаловать!' : 'Создать аккаунт' }}</h2>
                <p>{{ isLogin ? 'Войдите в систему для продолжения' : 'Присоединяйтесь к нашей платформе' }}</p>
              </div>

              <!-- Переключатель режимов -->
              <div class="mode-toggle">
                <q-btn-toggle v-model="mode" toggle-color="primary" :options="[
                  { label: 'Вход', value: 'login' },
                  { label: 'Регистрация', value: 'register' }
                ]" spread no-caps class="full-width modern-toggle" unelevated />
              </div>

              <!-- Форма входа -->
              <q-form v-if="isLogin" @submit="handleLogin" class="auth-form">
                <q-input v-model="loginForm.email" label="Email" type="email" outlined
                  :rules="[val => !!val || 'Введите email']" class="form-input">
                  <template v-slot:prepend>
                    <q-icon name="email" />
                  </template>
                </q-input>

                <q-input v-model="loginForm.password" label="Пароль" :type="showPassword ? 'text' : 'password'" outlined
                  :rules="[val => !!val || 'Введите пароль']" class="form-input">
                  <template v-slot:prepend>
                    <q-icon name="lock" />
                  </template>
                  <template v-slot:append>
                    <q-icon :name="showPassword ? 'visibility_off' : 'visibility'" class="cursor-pointer"
                      @click="showPassword = !showPassword" />
                  </template>
                </q-input>

                <q-btn type="submit" color="primary" label="Войти" class="submit-btn" :loading="loading" size="lg"
                  unelevated no-caps />
              </q-form>

              <!-- Форма регистрации -->
              <q-form v-else @submit="handleRegister" class="auth-form">
                <q-input v-model="registerForm.username" label="Имя пользователя" outlined
                  :rules="[val => !!val || 'Введите имя пользователя']" class="form-input">
                  <template v-slot:prepend>
                    <q-icon name="person" />
                  </template>
                </q-input>

                <q-input v-model="registerForm.name" label="Полное имя" outlined
                  :rules="[val => !!val || 'Введите полное имя']" class="form-input">
                  <template v-slot:prepend>
                    <q-icon name="badge" />
                  </template>
                </q-input>

                <q-input v-model="registerForm.email" label="Email" type="email" outlined
                  :rules="[val => !!val || 'Введите email']" class="form-input">
                  <template v-slot:prepend>
                    <q-icon name="email" />
                  </template>
                </q-input>

                <q-input v-model="registerForm.password" label="Пароль" :type="showPassword ? 'text' : 'password'"
                  outlined :rules="[val => val.length >= 6 || 'Минимум 6 символов']" class="form-input">
                  <template v-slot:prepend>
                    <q-icon name="lock" />
                  </template>
                  <template v-slot:append>
                    <q-icon :name="showPassword ? 'visibility_off' : 'visibility'" class="cursor-pointer"
                      @click="showPassword = !showPassword" />
                  </template>
                </q-input>

                <q-input v-model="registerForm.confirmPassword" label="Подтвердите пароль"
                  :type="showPassword ? 'text' : 'password'" outlined
                  :rules="[val => val === registerForm.password || 'Пароли не совпадают']" class="form-input">
                  <template v-slot:prepend>
                    <q-icon name="lock" />
                  </template>
                </q-input>

                <q-btn type="submit" color="primary" label="Создать аккаунт" class="submit-btn" :loading="loading"
                  size="lg" unelevated no-caps />
              </q-form>
            </div>
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'
import { useQuasar } from 'quasar'

const router = useRouter()
const authStore = useAuthStore()
const $q = useQuasar()

const mode = ref('login')
const showPassword = ref(false)
const loading = ref(false)

const isLogin = computed(() => mode.value === 'login')

const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  username: '',
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const features = [
  {
    icon: 'analytics',
    title: 'ИИ Прогнозирование',
    description: 'Машинное обучение для точного предсказания пожаров'
  },
  {
    icon: 'map',
    title: 'Интерактивные карты',
    description: 'Визуализация рисков в реальном времени'
  },
  {
    icon: 'notifications',
    title: 'Мгновенные уведомления',
    description: 'Оперативные оповещения о критических ситуациях'
  },
  {
    icon: 'security',
    title: 'Надежная защита',
    description: 'Безопасность данных на уровне государственных стандартов'
  }
]

const stats = [
  { value: '99.2%', label: 'Точность' },
  { value: '24/7', label: 'Мониторинг' },
  { value: '< 1мин', label: 'Отклик' },
  { value: '500+', label: 'Регионов' }
]



function getParticleStyle() {
  return {
    left: Math.random() * 100 + '%',
    animationDelay: Math.random() * 3 + 's',
    animationDuration: (Math.random() * 3 + 2) + 's'
  }
}

async function handleLogin() {
  loading.value = true
  try {
    console.log('Starting login process...')
    await authStore.login(loginForm.value.email, loginForm.value.password)

    console.log('Login completed, auth state:', {
      isAuthenticated: authStore.isAuthenticated,
      user: authStore.user,
      token: authStore.token ? 'exists' : 'missing'
    })

    const redirectPath = router.currentRoute.value.query.redirect || '/'
    console.log('Redirecting to:', redirectPath)

    $q.notify({
      color: 'positive',
      message: 'Добро пожаловать в FireForceAI!',
      icon: 'check_circle',
      position: 'top'
    })

    await router.replace(redirectPath)
    console.log('Navigation completed')
  } catch (error) {
    console.error('Login error:', error)
    $q.notify({
      color: 'negative',
      message: error.response?.data?.detail || 'Ошибка входа. Проверьте данные.',
      icon: 'error',
      position: 'top'
    })
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  loading.value = true
  try {
    await authStore.register({
      username: registerForm.value.username,
      full_name: registerForm.value.name,
      email: registerForm.value.email,
      password: registerForm.value.password
    })

    $q.notify({
      color: 'positive',
      message: 'Аккаунт успешно создан! Теперь войдите в систему.',
      icon: 'check_circle',
      position: 'top'
    })

    mode.value = 'login'
    loginForm.value.email = registerForm.value.email
    loginForm.value.password = ''

    registerForm.value = {
      username: '',
      name: '',
      email: '',
      password: '',
      confirmPassword: ''
    }
  } catch (error) {
    console.error('Registration error:', error)
    $q.notify({
      color: 'negative',
      message: error.response?.data?.detail || 'Ошибка регистрации. Попробуйте еще раз.',
      icon: 'error',
      position: 'top'
    })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.background-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.fire-particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: float infinite ease-in-out;
}

@keyframes float {

  0%,
  100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0;
  }

  50% {
    transform: translateY(-100px) rotate(180deg);
    opacity: 1;
  }
}

.auth-container {
  display: flex;
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
}

.info-section {
  flex: 1;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: white;
}

.logo-section {
  margin-bottom: 40px;
  text-align: center;
}

.logo-text {
  font-size: 2.8rem;
  font-weight: 700;
  margin: 15px 0 8px 0;
  background: linear-gradient(45deg, #fff, #f0f0f0);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.tagline {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0;
}

.fire-icon-container {
  display: inline-block;
  margin-bottom: 10px;
}

.fire-icon {
  color: #ff6b35;
  animation: fireFlicker 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  filter: drop-shadow(0 0 15px rgba(255, 107, 53, 0.6));
  transform-origin: center bottom;
}

@keyframes fireFlicker {
  0% {
    color: #ff6b35;
    transform: scale(1) rotate(-0.5deg) translateY(0px);
    filter: drop-shadow(0 0 15px rgba(255, 107, 53, 0.6));
  }

  15% {
    color: #ff8c42;
    transform: scale(1.02) rotate(0.3deg) translateY(-1px);
    filter: drop-shadow(0 0 18px rgba(255, 140, 66, 0.7));
  }

  30% {
    color: #ffa726;
    transform: scale(1.05) rotate(-0.2deg) translateY(-2px);
    filter: drop-shadow(0 0 22px rgba(255, 167, 38, 0.8));
  }

  45% {
    color: #ff7043;
    transform: scale(1.03) rotate(0.4deg) translateY(-1px);
    filter: drop-shadow(0 0 20px rgba(255, 112, 67, 0.7));
  }

  60% {
    color: #ff5722;
    transform: scale(0.98) rotate(-0.3deg) translateY(0px);
    filter: drop-shadow(0 0 16px rgba(255, 87, 34, 0.6));
  }

  75% {
    color: #ff6b35;
    transform: scale(1.01) rotate(0.2deg) translateY(-1px);
    filter: drop-shadow(0 0 19px rgba(255, 107, 53, 0.7));
  }

  90% {
    color: #ff8c42;
    transform: scale(1.04) rotate(-0.1deg) translateY(-2px);
    filter: drop-shadow(0 0 21px rgba(255, 140, 66, 0.75));
  }

  100% {
    color: #ff6b35;
    transform: scale(1) rotate(-0.5deg) translateY(0px);
    filter: drop-shadow(0 0 15px rgba(255, 107, 53, 0.6));
  }
}

.features {
  margin-bottom: 40px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;

  .q-icon {
    margin-right: 15px;
    margin-top: 3px;
  }

  h3 {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0 0 5px 0;
  }

  p {
    font-size: 0.9rem;
    opacity: 0.8;
    margin: 0;
    line-height: 1.4;
  }
}

.stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 3px;
}

.stat-label {
  font-size: 0.8rem;
  opacity: 0.8;
}

.form-section {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

body.body--dark .form-section {
  background: rgba(30, 41, 59, 0.95);
  color: #f8fafc;
}

.form-container {
  width: 100%;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;

  h2 {
    font-size: 2rem;
    font-weight: 700;
    color: #333;
    margin: 0 0 10px 0;
  }

  p {
    color: #666;
    margin: 0;
  }
}

body.body--dark .form-header {
  h2 {
    color: #f8fafc;
  }

  p {
    color: #cbd5e1;
  }
}

.mode-toggle {
  margin-bottom: 30px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-input {
  .q-field__control {
    border-radius: 12px;
  }
}

.modern-toggle {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.submit-btn {
  border-radius: 12px;
  padding: 12px;
  font-weight: 600;
  margin-top: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
  }
}

@media (max-width: 1024px) {
  .auth-container {
    flex-direction: column;
  }

  .info-section {
    padding: 40px;
    text-align: center;
  }

  .logo-text {
    font-size: 2.5rem;
  }

  .features {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-bottom: 40px;
  }

  .feature-item {
    margin-bottom: 0;
  }
}

@media (max-width: 768px) {
  .info-section {
    padding: 30px 20px;
  }

  .form-section {
    padding: 30px 20px;
  }

  .features {
    grid-template-columns: 1fr;
  }

  .stats {
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
  }

  .stat-number {
    font-size: 1.8rem;
  }
}
</style>