<template>
    <q-page class="analytics-page q-pa-lg">
        <!-- Заголовок страницы -->
        <div class="page-header q-mb-xl">
            <div class="text-h4 text-weight-bold text-primary">Аналитика</div>
            <div class="text-subtitle1 text-grey-6 q-mt-sm">Статистический анализ и прогнозирование пожаров</div>
        </div>

        <div class="row q-col-gutter-xl">
            <!-- Header -->
            <div class="col-12">
                <q-card class="dashboard-card filters-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="analytics" size="28px" color="primary" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Аналитика пожаров</div>
                                <div class="text-caption text-grey-6">Статистический анализ и прогнозирование</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <div class="row q-col-gutter-lg">
                            <div class="col-12 col-md-4">
                                <q-select outlined dense v-model="timeRange" :options="timeRangeOptions"
                                    label="Временной диапазон" class="filter-input" />
                            </div>
                            <div class="col-12 col-md-4">
                                <q-select outlined dense v-model="region" :options="regionOptions" label="Регион" class="filter-input" />
                            </div>
                            <div class="col-12 col-md-4">
                                <q-btn color="primary" label="Обновить данные" class="full-width refresh-btn"
                                    @click="refreshData" :loading="loading" size="lg" />
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>

            <!-- Key Metrics -->
            <div class="col-12">
                <div class="row q-col-gutter-lg">
                    <div class="col-12 col-md-3" v-for="(metric, index) in keyMetrics" :key="index">
                        <q-card class="dashboard-card metric-card">
                            <q-card-section class="card-content text-center">
                                <div class="metric-icon q-mb-md">
                                    <q-icon :name="metric.icon" size="48px" :color="metric.iconColor" />
                                </div>
                                <div class="text-h4 text-weight-bold" :class="metric.color">{{ metric.value }}</div>
                                <div class="text-subtitle1 text-grey-6">{{ metric.label }}</div>
                                <div class="trend-indicator q-mt-sm" v-if="metric.trend !== undefined">
                                    <q-icon :name="metric.trend > 0 ? 'arrow_upward' : 'arrow_downward'"
                                        :color="metric.trend > 0 ? 'negative' : 'positive'" size="sm" />
                                    <span :class="metric.trend > 0 ? 'text-negative' : 'text-positive'">
                                        {{ Math.abs(metric.trend) }}% от прошлого периода
                                    </span>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                </div>
            </div>

            <!-- Main Charts -->
            <div class="col-12 col-lg-8">
                <q-card class="dashboard-card chart-card q-mb-lg">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="show_chart" size="28px" color="blue" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Динамика пожаров</div>
                                <div class="text-caption text-grey-6">Анализ тенденций и паттернов</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-tabs v-model="chartTab" class="text-grey analytics-tabs" active-color="primary" indicator-color="primary"
                            align="left">
                            <q-tab name="frequency" label="Частота" />
                            <q-tab name="area" label="Площадь" />
                            <q-tab name="severity" label="Серьезность" />
                        </q-tabs>
                        <q-separator class="q-my-md" />
                        <div style="height: 300px" class="chart-placeholder">
                            <div class="text-center text-grey q-pt-xl">
                                <q-icon name="show_chart" size="64px" class="q-mb-md" />
                                <div class="text-h6">Здесь будет график динамики пожаров</div>
                                <div class="text-caption">Интерактивная визуализация данных</div>
                            </div>
                        </div>
                    </q-card-section>
                </q-card>

                <q-card class="dashboard-card correlation-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="scatter_plot" size="28px" color="green" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Корреляционный анализ</div>
                                <div class="text-caption text-grey-6">Связи между факторами</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <div class="row q-col-gutter-lg">
                            <div class="col-12 col-md-6">
                                <q-select outlined dense v-model="xAxis" :options="correlationOptions" label="Ось X" class="filter-input" />
                            </div>
                            <div class="col-12 col-md-6">
                                <q-select outlined dense v-model="yAxis" :options="correlationOptions" label="Ось Y" class="filter-input" />
                            </div>
                        </div>
                        <div style="height: 300px" class="chart-placeholder q-mt-lg">
                            <div class="text-center text-grey q-pt-xl">
                                <q-icon name="scatter_plot" size="64px" class="q-mb-md" />
                                <div class="text-h6">Здесь будет график корреляции</div>
                                <div class="text-caption">Анализ взаимосвязей факторов</div>
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>

            <!-- Sidebar -->
            <div class="col-12 col-lg-4">
                <!-- Top Regions -->
                <q-card class="dashboard-card regions-card q-mb-lg">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="location_on" size="28px" color="orange" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Регионы с высоким риском</div>
                                <div class="text-caption text-grey-6">Топ проблемных зон</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-list separator class="regions-list">
                            <q-item v-for="(region, index) in topRiskRegions" :key="index" class="region-item">
                                <q-item-section avatar>
                                    <q-avatar :color="region.color" text-color="white" size="32px" class="region-avatar">
                                        {{ index + 1 }}
                                    </q-avatar>
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">{{ region.name }}</q-item-label>
                                    <q-item-label caption class="text-grey-6">{{ region.fires }} пожаров за период</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-badge :color="region.riskColor" rounded class="risk-badge">
                                        {{ region.riskLevel }}
                                    </q-badge>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                </q-card>

                <!-- Weather Impact -->
                <q-card class="dashboard-card weather-card q-mb-lg">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="wb_sunny" size="28px" color="yellow" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Влияние погоды</div>
                                <div class="text-caption text-grey-6">Факторы окружающей среды</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-list separator class="weather-list">
                            <q-item v-for="(factor, index) in weatherFactors" :key="index" class="weather-item">
                                <q-item-section avatar>
                                    <q-icon :name="factor.icon" :color="factor.color" size="md" />
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">{{ factor.name }}</q-item-label>
                                    <q-item-label caption class="text-grey-6">{{ factor.description }}</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-circular-progress 
                                        show-value 
                                        font-size="12px" 
                                        :value="factor.impact" 
                                        size="40px"
                                        :color="factor.color" 
                                        track-color="grey-3"
                                        class="impact-progress"
                                    >
                                        {{ factor.impact }}%
                                    </q-circular-progress>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                </q-card>

                <!-- Recent Trends -->
                <q-card class="dashboard-card trends-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="trending_up" size="28px" color="purple" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Последние тенденции</div>
                                <div class="text-caption text-grey-6">Ключевые изменения</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-list separator class="trends-list">
                            <q-item v-for="(trend, index) in recentTrends" :key="index" class="trend-item">
                                <q-item-section avatar>
                                    <q-icon :name="trend.icon" :color="trend.color" />
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">{{ trend.title }}</q-item-label>
                                    <q-item-label caption class="text-grey-6">{{ trend.description }}</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <div class="text-right">
                                        <div :class="`text-${trend.changeColor}`" class="text-weight-bold trend-change">
                                            {{ trend.change }}
                                        </div>
                                        <div class="text-caption text-grey-5">
                                            {{ trend.period }}
                                        </div>
                                    </div>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                </q-card>
            </div>
        </div>
    </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();

const loading = ref(false);
const chartTab = ref('frequency');
const timeRange = ref({ label: 'Последние 12 месяцев', value: '12m' });
const region = ref({ label: 'Вся Россия', value: 'all' });
const xAxis = ref({ label: 'Температура', value: 'temperature' });
const yAxis = ref({ label: 'Количество пожаров', value: 'fire_count' });
const keyMetrics = ref([]);
const topRiskRegions = ref([]);
const weatherFactors = ref([]);
const recentTrends = ref([]);

const timeRangeOptions = [
    { label: 'Последние 30 дней', value: '30d' },
    { label: 'Последние 3 месяца', value: '3m' },
    { label: 'Последние 6 месяцев', value: '6m' },
    { label: 'Последние 12 месяцев', value: '12m' },
    { label: 'Последние 5 лет', value: '5y' }
];

const regionOptions = [
    { label: 'Вся Россия', value: 'all' },
    { label: 'Красноярский край', value: 'krasnoyarsk' },
    { label: 'Иркутская область', value: 'irkutsk' },
    { label: 'Республика Саха (Якутия)', value: 'yakutia' },
    { label: 'Забайкальский край', value: 'zabaykalsky' },
    { label: 'Амурская область', value: 'amur' }
];

const correlationOptions = [
    { label: 'Температура', value: 'temperature' },
    { label: 'Влажность', value: 'humidity' },
    { label: 'Скорость ветра', value: 'wind_speed' },
    { label: 'Осадки', value: 'precipitation' },
    { label: 'Количество пожаров', value: 'fire_count' },
    { label: 'Площадь пожаров', value: 'fire_area' }
];

function initializeMockData() {
    topRiskRegions.value = [
        { name: 'Красноярский край', fires: 45, riskLevel: 'Высокий', riskColor: 'red', color: 'red' },
        { name: 'Иркутская область', fires: 38, riskLevel: 'Высокий', riskColor: 'red', color: 'orange' },
        { name: 'Республика Саха', fires: 32, riskLevel: 'Средний', riskColor: 'orange', color: 'amber' },
        { name: 'Забайкальский край', fires: 28, riskLevel: 'Средний', riskColor: 'orange', color: 'yellow' },
        { name: 'Амурская область', fires: 22, riskLevel: 'Низкий', riskColor: 'green', color: 'green' }
    ];

    weatherFactors.value = [
        { name: 'Температура', description: 'Высокие температуры', impact: 85, icon: 'thermostat', color: 'red' },
        { name: 'Влажность', description: 'Низкая влажность воздуха', impact: 72, icon: 'water_drop', color: 'blue' },
        { name: 'Ветер', description: 'Сильные ветра', impact: 68, icon: 'air', color: 'teal' },
        { name: 'Осадки', description: 'Отсутствие дождей', impact: 91, icon: 'grain', color: 'purple' }
    ];

    recentTrends.value = [
        { 
            title: 'Количество пожаров', 
            description: 'За последний месяц', 
            change: '+12%', 
            changeColor: 'negative',
            period: 'vs прошлый месяц',
            icon: 'local_fire_department',
            color: 'red'
        },
        { 
            title: 'Время реагирования', 
            description: 'Среднее время прибытия', 
            change: '-8%', 
            changeColor: 'positive',
            period: 'vs прошлый месяц',
            icon: 'schedule',
            color: 'green'
        },
        { 
            title: 'Площадь возгораний', 
            description: 'Общая площадь', 
            change: '+5%', 
            changeColor: 'negative',
            period: 'vs прошлый месяц',
            icon: 'landscape',
            color: 'orange'
        }
    ];
}

async function loadAnalyticsData() {
    loading.value = true;
    try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        keyMetrics.value = [
            { label: 'Всего пожаров', value: '156', color: 'text-primary', trend: 12, icon: 'fire_extinguisher', iconColor: 'red' },
            { label: 'Средняя площадь (га)', value: '24.5', color: 'text-orange', trend: -8, icon: 'landscape', iconColor: 'orange' },
            { label: 'Время реагирования (мин)', value: '18', color: 'text-purple', trend: -15, icon: 'schedule', iconColor: 'purple' },
            { label: 'Эффективность тушения', value: '94%', color: 'text-positive', trend: 3, icon: 'check_circle', iconColor: 'green' }
        ];

        initializeMockData();
        
        $q.notify({
            color: 'positive',
            message: 'Данные обновлены',
            icon: 'check_circle'
        });
    } catch (error) {
        console.error('Error loading analytics data:', error);
        $q.notify({
            color: 'negative',
            message: 'Ошибка загрузки аналитических данных',
            icon: 'error'
        });
    } finally {
        loading.value = false;
    }
}

function refreshData() {
    loadAnalyticsData();
}

onMounted(() => {
    initializeMockData();
    loadAnalyticsData();
});
</script>

<style lang="scss" scoped>
.analytics-page {
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

.filters-card {
  .filter-input {
    border-radius: 12px;
    
    .q-field__control {
      border-radius: 12px;
    }
  }
  
  .refresh-btn {
    border-radius: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(37, 99, 235, 0.3);
    }
  }
}

.metric-card {
  text-align: center;
  
  .metric-icon {
    margin-bottom: 1rem;
    transition: transform 0.3s ease;
  }
  
  .text-h4 {
    font-weight: 700;
    margin-bottom: 0.5rem;
  }
  
  &:hover {
    .metric-icon {
      transform: scale(1.1);
    }
  }
}

.chart-card {
  .analytics-tabs {
    .q-tab {
      border-radius: 8px;
      margin-right: 8px;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba(37, 99, 235, 0.1);
      }
    }
  }
  
  .chart-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    background: rgba(37, 99, 235, 0.05);
    border-radius: 12px;
    border: 2px dashed rgba(37, 99, 235, 0.2);
  }
}

.correlation-card {
  .chart-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    background: rgba(5, 150, 105, 0.05);
    border-radius: 12px;
    border: 2px dashed rgba(5, 150, 105, 0.2);
  }
}

.regions-card {
  .regions-list {
    .region-item {
      border-radius: 12px;
      margin: 8px 0;
      padding: 12px;
      transition: all 0.2s ease;
      border: 1px solid transparent;

      &:hover {
        background: rgba(37, 99, 235, 0.05);
        border-color: rgba(37, 99, 235, 0.1);
        transform: translateX(4px);
      }
    }

    .region-avatar {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .risk-badge {
      font-weight: 600;
      border-radius: 8px;
      padding: 4px 8px;
    }
  }
}

.weather-card {
  .weather-list {
    .weather-item {
      border-radius: 12px;
      margin: 8px 0;
      padding: 12px;
      transition: all 0.2s ease;
      border: 1px solid transparent;

      &:hover {
        background: rgba(37, 99, 235, 0.05);
        border-color: rgba(37, 99, 235, 0.1);
        transform: translateX(4px);
      }
    }

    .impact-progress {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
  }
}

.trends-card {
  .trends-list {
    .trend-item {
      border-radius: 12px;
      margin: 8px 0;
      padding: 12px;
      transition: all 0.2s ease;
      border: 1px solid transparent;

      &:hover {
        background: rgba(37, 99, 235, 0.05);
        border-color: rgba(37, 99, 235, 0.1);
        transform: translateX(4px);
      }
    }

    .trend-change {
      font-weight: 700;
    }
  }
}

.trend-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  margin-top: 0.5rem;

  .q-icon {
    margin-right: 4px;
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .page-header {
    padding: 1rem 0;
    
    .text-h4 {
      font-size: 1.75rem;
    }
  }
  
  .metric-card {
    .metric-icon {
      .q-icon {
        font-size: 32px;
      }
    }
  }
}
</style>