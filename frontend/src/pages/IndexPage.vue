<template>
  <q-page class="dashboard-page q-pa-lg">
    <!-- Заголовок страницы -->
    <div class="page-header q-mb-xl">
      <div class="text-h4 text-weight-bold text-primary">Панель управления</div>
      <div class="text-subtitle1 text-grey-6 q-mt-sm">Мониторинг и управление пожарной безопасностью</div>
    </div>

    <!-- Ключевые метрики KPI -->
    <div class="row q-col-gutter-lg q-mb-xl">
      <!-- Активные пожары -->
      <div class="col-12 col-sm-6 col-lg-3">
        <q-card class="metric-card fire-card">
          <q-card-section class="relative-position">
            <div class="absolute-full fire-bg">
              <q-icon name="local_fire_department" size="150px" class="text-white opacity-10" />
            </div>
            <div class="relative-position flex items-center justify-between q-mb-md">
              <q-icon name="local_fire_department" size="28px" class="text-white" />
              <span class="text-h3 text-weight-bold text-white">{{ keyMetrics[0].value }}</span>
            </div>
            <div class="text-h6 text-weight-medium q-mb-xs text-white">{{ keyMetrics[0].label }}</div>
            <div class="text-subtitle2 opacity-8 text-white">{{ keyMetrics[0].change }}</div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Зоны высокого риска -->
      <div class="col-12 col-sm-6 col-lg-3">
        <q-card class="metric-card warning-card">
          <q-card-section class="relative-position">
            <div class="absolute-full warning-bg">
              <q-icon name="warning" size="150px" class="text-white opacity-10" />
            </div>
            <div class="relative-position flex items-center justify-between q-mb-md">
              <q-icon name="warning" size="28px" class="text-white" />
              <span class="text-h3 text-weight-bold text-white">{{ keyMetrics[1].value }}</span>
            </div>
            <div class="text-h6 text-weight-medium q-mb-xs text-white">{{ keyMetrics[1].label }}</div>
            <div class="text-subtitle2 opacity-8 text-white">{{ keyMetrics[1].change }}</div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Точность прогноза -->
      <div class="col-12 col-sm-6 col-lg-3">
        <q-card class="metric-card accuracy-card">
          <q-card-section class="relative-position">
            <div class="absolute-full accuracy-bg">
              <q-icon name="trending_up" size="150px" class="text-white opacity-10" />
            </div>
            <div class="relative-position flex items-center justify-between q-mb-md">
              <q-icon name="trending_up" size="28px" class="text-white" />
              <span class="text-h3 text-weight-bold text-white">{{ keyMetrics[2].value }}</span>
            </div>
            <div class="text-h6 text-weight-medium q-mb-xs text-white">{{ keyMetrics[2].label }}</div>
            <div class="text-subtitle2 opacity-8 text-white">{{ keyMetrics[2].change }}</div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Активные команды -->
      <div class="col-12 col-sm-6 col-lg-3">
        <q-card class="metric-card teams-card">
          <q-card-section class="relative-position">
            <div class="absolute-full teams-bg">
              <q-icon name="people" size="150px" class="text-white opacity-10" />
            </div>
            <div class="relative-position flex items-center justify-between q-mb-md">
              <q-icon name="people" size="28px" class="text-white" />
              <span class="text-h3 text-weight-bold text-white">{{ keyMetrics[3].value }}</span>
            </div>
            <div class="text-h6 text-weight-medium q-mb-xs text-white">{{ keyMetrics[3].label }}</div>
            <div class="text-subtitle2 opacity-8 text-white">{{ keyMetrics[3].change }}</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Основная структура: карта слева (2/3) + блоки справа (1/3) -->
    <div class="row q-col-gutter-xl dashboard-content">
      <!-- Левая часть - Карта (2/3 экрана) -->
      <div class="col-12 col-lg-8 map-column">
        <q-card class="dashboard-card map-card full-height">
          <q-card-section class="card-header">
            <div class="row items-center">
              <q-icon name="map" size="28px" color="primary" class="q-mr-md" />
              <div>
                <div class="text-h6 text-weight-bold">Карта пожарной опасности</div>
                <div class="text-caption text-grey-6">Интерактивная карта с актуальными данными</div>
              </div>
            </div>
          </q-card-section>
          <q-card-section class="card-content q-pa-none">
            <div class="col">
              <DashboardMap />
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Правая часть - Блоки (1/3 экрана) -->
      <div class="col-12 col-lg-4 sidebar-column">
        <!-- Точечный прогноз -->
        <q-card class="dashboard-card prediction-card q-mb-lg">
          <q-card-section class="card-header">
            <div class="row items-center">
              <q-icon name="trending_up" size="28px" color="white" class="q-mr-md" />
              <div>
                <div class="text-h6 text-weight-bold text-white">Точечный прогноз</div>
                <div class="text-caption text-white opacity-8">Получите прогноз пожарной опасности</div>
              </div>
            </div>
          </q-card-section>
          <q-card-section class="card-content text-center">
            <div class="text-body2 q-mb-lg text-white opacity-9">
              Получите прогноз пожарной опасности для конкретной точки
            </div>
            <q-btn
              color="white"
              text-color="primary"
              label="Узнать прогноз"
              icon="location_on"
              @click="goToPredictions"
              no-caps
              unelevated
              size="lg"
              class="full-width q-py-md prediction-btn"
            />
          </q-card-section>
        </q-card>

        <!-- Тренды пожаров -->
        <q-card class="dashboard-card q-mb-lg">
          <q-card-section class="card-header">
            <div class="row items-center">
              <q-icon name="analytics" size="28px" color="green" class="q-mr-md" />
              <div>
                <div class="text-h6 text-weight-bold">Тренды пожаров</div>
                <div class="text-caption text-grey-6">Динамика за последние 30 дней</div>
              </div>
            </div>
          </q-card-section>
          <q-card-section class="card-content">
            <div class="text-center">
              <div class="text-h4 text-primary text-weight-bold">{{ fireStats.totalFires }}</div>
              <div class="text-caption text-grey-6">Всего пожаров за месяц</div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Последние события -->
        <q-card class="dashboard-card">
          <q-card-section class="card-header">
            <div class="row items-center">
              <q-icon name="notifications" size="28px" color="orange" class="q-mr-md" />
              <div>
                <div class="text-h6 text-weight-bold">Последние события</div>
                <div class="text-caption text-grey-6">Актуальные уведомления</div>
              </div>
            </div>
          </q-card-section>
          <q-card-section class="card-content">
            <div class="events-list">
              <div class="event-item" v-for="event in recentEvents.slice(0, 4)" :key="event.id">
                <div class="event-indicator" :class="`event-indicator--${event.type}`"></div>
                <div class="event-content">
                  <div class="text-body2 text-weight-medium">{{ event.title }}</div>
                  <div class="text-caption text-grey-6">{{ event.description }}</div>
                  <div class="text-caption text-grey-5">{{ formatTime(event.time) }}</div>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DashboardMap from 'src/components/dashboard/DashboardMap.vue'
import ApiService from 'src/services/api'
import { initColorScheme } from 'src/utils/colorScheme';

const $router = useRouter()

function goToPredictions() {
  $router.push('/predictions')
}

const keyMetrics = ref([
  {
    value: '12',
    label: 'Активные пожары',
    change: '↑ 3 за последний час'
  },
  {
    value: '28',
    label: 'Зоны высокого риска',
    change: '↓ 2 с вчерашнего дня'
  },
  {
    value: '94.2%',
    label: 'Точность прогноза',
    change: 'За последние 30 дней'
  },
  {
    value: '15',
    label: 'Активные команды',
    change: '98% готовности'
  }
])

const fireStats = ref({
  totalFires: 156
})

const recentEvents = ref([
  {
    id: 1,
    type: 'fire',
    title: 'Новый пожар обнаружен',
    description: 'Красноярский край, площадь ~5 га',
    time: new Date(Date.now() - 15 * 60 * 1000)
  },
  {
    id: 2,
    type: 'warning',
    title: 'Повышенный риск пожара',
    description: 'Иркутская область, высокие риски 4.5',
    time: new Date(Date.now() - 32 * 60 * 1000)
  },
  {
    id: 3,
    type: 'success',
    title: 'Пожар локализован',
    description: 'Томская область, площадь 8 га',
    time: new Date(Date.now() - 45 * 60 * 1000)
  },
  {
    id: 4,
    type: 'info',
    title: 'Система обновлена',
    description: 'Точность прогнозов повышена до 94.2%',
    time: new Date(Date.now() - 2 * 60 * 60 * 1000)
  }
])

function formatTime(date) {
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  
  if (minutes < 60) {
    return `${minutes} мин назад`
  } else {
    return `${hours} ч назад`
  }
}

async function loadDashboardData() {
  try {
    const systemStats = await ApiService.getSystemStats()
    console.log('System stats loaded:', systemStats)
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  }
}

onMounted(() => {
  // Инициализируем цветовую схему
  initColorScheme();
  loadDashboardData()
})
</script>

<style lang="scss" scoped>
.dashboard-page {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.03) 0%, rgba(5, 150, 105, 0.03) 100%);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  padding: 2rem 0;
  
  .text-h4 {
    background: linear-gradient(135deg, #2563eb, #059669);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

.metric-card {
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  }
}

.fire-card {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
}

.warning-card {
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
}

.accuracy-card {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
}

.teams-card {
  background: linear-gradient(135deg, #27ae60 0%, #16a085 100%);
}

.opacity-8 {
  opacity: 0.8;
}

.opacity-9 {
  opacity: 0.9;
}

.opacity-10 {
  opacity: 0.1;
}

.dashboard-content {
  align-items: stretch;
}

.map-column,
.sidebar-column {
  display: flex;
  flex-direction: column;
}

.dashboard-card {
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
  }

  .card-header {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.1), rgba(5, 150, 105, 0.1));
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 1.5rem;
  }

  .card-content {
    padding: 1.5rem;
  }
}

.map-card {
  &.full-height {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .card-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    
    .col {
      flex: 1;
      display: flex;
      flex-direction: column;
      
      > * {
        flex: 1;
        height: 100%;
      }
    }
  }
}

.prediction-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  
  .prediction-btn {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    transition: all 0.3s ease;
    border-radius: 12px;
    
    &:hover {
      background: rgba(255, 255, 255, 0.3);
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(255, 255, 255, 0.2);
    }
    
    &:active {
      transform: translateY(0);
    }
  }
}

.events-list {
  .event-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 16px 0;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;

    &:last-child {
      border-bottom: none;
    }

    &:hover {
      background: rgba(37, 99, 235, 0.05);
      border-radius: 8px;
      padding-left: 8px;
      padding-right: 8px;
      margin-left: -8px;
      margin-right: -8px;
    }
  }

  .event-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-top: 6px;
    flex-shrink: 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

    &--fire {
      background: #e74c3c;
    }

    &--warning {
      background: #f39c12;
    }

    &--success {
      background: #27ae60;
    }

    &--info {
      background: #3498db;
    }
  }

  .event-content {
    flex: 1;
    min-width: 0;
  }
}

@media (max-width: 1023px) {
  .dashboard-content {
    flex-direction: column;
  }
  
  .map-card.full-height {
    height: 500px;
  }
}

@media (max-width: 768px) {
  .map-card.full-height {
    height: 350px;
  }
}

:deep(.map-container) {
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
}

:deep(#dashboard-map-container) {
  height: 100% !important;
  flex: 1 !important;
  min-height: 0 !important;
}

:deep(.leaflet-container) {
  height: 100% !important;
  width: 100% !important;
  min-height: 0 !important;
}

:deep(#dashboard-map-container[style]) {
  height: 100% !important;
}
</style>
Глобальные стили для растягивания Leaflet карты
:deep(.map-container) {
  height: 100% !important;
  display: flex;
  flex-direction: column;
}

:deep(#dashboard-map-container) {
  height: 100% !important;
  flex: 1;
}

:deep(.leaflet-container) {
  height: 100% !important;
  width: 100% !important;
}