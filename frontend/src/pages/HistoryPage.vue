<template>
    <q-page class="history-page q-pa-lg">
        <!-- Заголовок страницы -->
        <div class="page-header q-mb-xl">
            <div class="text-h4 text-weight-bold text-primary">История пожаров</div>
            <div class="text-subtitle1 text-grey-6 q-mt-sm">Архив данных о пожарах и их анализ</div>
        </div>

        <div class="row q-col-gutter-xl">
            <!-- Filters -->
            <div class="col-12">
                <q-card class="dashboard-card filters-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="filter_list" size="28px" color="primary" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Фильтры и поиск</div>
                                <div class="text-caption text-grey-6">Настройте параметры поиска</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <div class="row q-col-gutter-lg">
                            <div class="col-12 col-md-3">
                                <q-input outlined dense v-model="filters.search" label="Поиск по региону" clearable class="filter-input">
                                    <template v-slot:append>
                                        <q-icon name="search" />
                                    </template>
                                </q-input>
                            </div>
                            <div class="col-12 col-md-3">
                                <q-select outlined dense v-model="filters.year" :options="yearOptions" label="Год" class="filter-input" />
                            </div>
                            <div class="col-12 col-md-3">
                                <q-select outlined dense v-model="filters.severity" :options="severityOptions"
                                    label="Серьезность" class="filter-input" />
                            </div>
                            <div class="col-12 col-md-3">
                                <q-btn color="primary" label="Применить фильтры" class="full-width filter-btn"
                                    @click="applyFilters" size="lg" />
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>

            <!-- Statistics -->
            <div class="col-12">
                <div class="row q-col-gutter-lg">
                    <div class="col-12 col-md-3" v-for="(stat, index) in statistics" :key="index">
                        <q-card class="dashboard-card stat-card">
                            <q-card-section class="card-content text-center">
                                <div class="stat-icon q-mb-md">
                                    <q-icon :name="stat.icon" size="48px" :color="stat.iconColor" />
                                </div>
                                <div class="text-h4 text-weight-bold" :class="stat.color">{{ stat.value }}</div>
                                <div class="text-subtitle1 text-grey-6">{{ stat.label }}</div>
                            </q-card-section>
                        </q-card>
                    </div>
                </div>
            </div>

            <!-- Chart -->
            <div class="col-12 col-lg-8">
                <q-card class="dashboard-card chart-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="show_chart" size="28px" color="blue" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Динамика пожаров по годам</div>
                                <div class="text-caption text-grey-6">Статистика за последние 5 лет</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content" style="height: 300px">
                        <div class="text-center text-grey q-pt-xl">
                            <q-icon name="show_chart" size="64px" class="q-mb-md" />
                            <div class="text-h6">Здесь будет график динамики пожаров</div>
                            <div class="text-caption">Интерактивная визуализация данных</div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>

            <!-- Top Regions -->
            <div class="col-12 col-lg-4">
                <q-card class="dashboard-card regions-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="location_on" size="28px" color="orange" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Топ регионов</div>
                                <div class="text-caption text-grey-6">Наибольшее число пожаров</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-list separator class="regions-list">
                            <q-item v-for="(region, index) in topRegions" :key="index" class="region-item">
                                <q-item-section avatar>
                                    <q-avatar color="primary" text-color="white" class="region-avatar">{{ index + 1 }}</q-avatar>
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">{{ region.name }}</q-item-label>
                                    <q-item-label caption class="text-grey-6">{{ region.count }} пожаров</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-linear-progress size="xs" :value="region.count / maxRegionCount" color="orange"
                                        class="region-progress" />
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                </q-card>
            </div>

            <!-- Data Table -->
            <div class="col-12">
                <q-card class="dashboard-card table-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="table_chart" size="28px" color="green" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Данные о пожарах</div>
                                <div class="text-caption text-grey-6">Детальная информация</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-table :rows="fireData" :columns="columns" row-key="id" :pagination="pagination"
                            :loading="loading" :filter="filters.search" class="history-table" flat bordered>
                            <template v-slot:body-cell-risk_level="props">
                                <q-td :props="props">
                                    <q-badge :color="getSeverityColor(props.value)" class="severity-badge">{{ props.value }}</q-badge>
                                </q-td>
                            </template>
                            <template v-slot:body-cell-actions="props">
                                <q-td :props="props">
                                    <q-btn flat round dense icon="visibility" @click="viewDetails(props.row)" class="action-btn" />
                                </q-td>
                            </template>
                        </q-table>
                    </q-card-section>
                </q-card>
            </div>
        </div>

        <!-- Details Dialog -->
        <q-dialog v-model="detailsDialog" persistent>
            <q-card class="dashboard-card details-dialog" style="min-width: 400px">
                <q-card-section class="card-header">
                    <div class="row items-center">
                        <q-icon name="info" size="28px" color="primary" class="q-mr-md" />
                        <div class="text-h6 text-weight-bold">Детали пожара #{{ selectedFire?.id }}</div>
                        <q-space />
                        <q-btn icon="close" flat round dense v-close-popup />
                    </div>
                </q-card-section>
                <q-card-section class="card-content" v-if="selectedFire">
                    <div class="detail-item q-mb-md">
                        <div class="text-caption text-grey-6">Координаты</div>
                        <div class="text-body1">{{ selectedFire.latitude }}, {{ selectedFire.longitude }}</div>
                    </div>
                    <div class="detail-item q-mb-md">
                        <div class="text-caption text-grey-6">Дата</div>
                        <div class="text-body1">{{ selectedFire.created_at }}</div>
                    </div>
                    <div class="detail-item q-mb-md">
                        <div class="text-caption text-grey-6">Уровень риска</div>
                        <div>
                            <q-badge :color="getSeverityColor(selectedFire.risk_level)" class="severity-badge">{{ selectedFire.risk_level }}</q-badge>
                        </div>
                    </div>
                    <div class="detail-item q-mb-md">
                        <div class="text-caption text-grey-6">Температура</div>
                        <div class="text-body1">{{ selectedFire.temperature }}°C</div>
                    </div>
                    <div class="detail-item q-mb-md">
                        <div class="text-caption text-grey-6">Влажность</div>
                        <div class="text-body1">{{ selectedFire.humidity }}%</div>
                    </div>
                    <div class="detail-item q-mb-md">
                        <div class="text-caption text-grey-6">Скорость ветра</div>
                        <div class="text-body1">{{ selectedFire.wind_speed }} м/с</div>
                    </div>
                </q-card-section>
                <q-card-actions align="right" class="card-content">
                    <q-btn flat label="Закрыть" color="primary" v-close-popup />
                </q-card-actions>
            </q-card>
        </q-dialog>
    </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();

const loading = ref(false);
const filters = ref({
    search: '',
    year: { label: 'Все годы', value: 'all' },
    severity: { label: 'Все уровни', value: 'all' }
});
const detailsDialog = ref(false);
const selectedFire = ref(null);
const fireData = ref([]);

const yearOptions = [
    { label: 'Все годы', value: 'all' },
    { label: '2025', value: '2025' },
    { label: '2024', value: '2024' },
    { label: '2023', value: '2023' },
    { label: '2022', value: '2022' },
    { label: '2021', value: '2021' }
];

const severityOptions = [
    { label: 'Все уровни', value: 'all' },
    { label: 'Низкий', value: 'low' },
    { label: 'Средний', value: 'medium' },
    { label: 'Высокий', value: 'high' },
    { label: 'Критический', value: 'critical' }
];

const columns = [
    { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
    { name: 'created_at', label: 'Дата', field: 'created_at', sortable: true, align: 'left' },
    { name: 'latitude', label: 'Широта', field: 'latitude', sortable: true, align: 'right' },
    { name: 'longitude', label: 'Долгота', field: 'longitude', sortable: true, align: 'right' },
    { name: 'risk_level', label: 'Уровень риска', field: 'risk_level', sortable: true, align: 'center' },
    { name: 'temperature', label: 'Температура', field: 'temperature', sortable: true, align: 'right' },
    { name: 'actions', label: 'Действия', field: 'actions', align: 'center' }
];

const pagination = ref({
    sortBy: 'created_at',
    descending: true,
    page: 1,
    rowsPerPage: 10
});

const statistics = [
    { label: 'Всего пожаров', value: '1,245', color: 'text-primary', icon: 'fire_truck', iconColor: 'primary' },
    { label: 'Площадь (га)', value: '28,350', color: 'text-orange', icon: 'landscape', iconColor: 'orange' },
    { label: 'Критических', value: '187', color: 'text-negative', icon: 'warning', iconColor: 'negative' },
    { label: 'Потушено', value: '1,198', color: 'text-positive', icon: 'check_circle', iconColor: 'positive' }
];

const topRegions = [
    { name: 'Красноярский край', count: 312 },
    { name: 'Иркутская область', count: 245 },
    { name: 'Республика Саха (Якутия)', count: 198 },
    { name: 'Забайкальский край', count: 156 },
    { name: 'Амурская область', count: 134 }
];

const maxRegionCount = computed(() => {
    return Math.max(...topRegions.map(r => r.count));
});

function getSeverityColor(severity) {
    switch (severity) {
        case 'low': return 'green';
        case 'medium': return 'yellow';
        case 'high': return 'orange';
        case 'critical': return 'red';
        default: return 'grey';
    }
}

async function loadFireHistory() {
    loading.value = true;
    try {
        // Временно используем мок-данные вместо API
        const mockFireData = [
            {
                id: 1,
                date: '2024-01-15',
                location: 'Красноярский край',
                severity: 'high',
                area_affected: 1500,
                status: 'extinguished',
                coordinates: { lat: 56.0184, lng: 92.8672 }
            },
            {
                id: 2,
                date: '2024-01-14',
                location: 'Иркутская область',
                severity: 'critical',
                area_affected: 2500,
                status: 'active',
                coordinates: { lat: 52.2864, lng: 104.3050 }
            },
            {
                id: 3,
                date: '2024-01-13',
                location: 'Республика Саха',
                severity: 'medium',
                area_affected: 800,
                status: 'extinguished',
                coordinates: { lat: 66.2654, lng: 129.6755 }
            },
            {
                id: 4,
                date: '2024-01-12',
                location: 'Амурская область',
                severity: 'low',
                area_affected: 300,
                status: 'extinguished',
                coordinates: { lat: 50.2904, lng: 127.5272 }
            }
        ];
        
        fireData.value = mockFireData;
    } catch (error) {
        console.error('Error loading fire history:', error);
        $q.notify({
            color: 'negative',
            message: 'Ошибка загрузки данных',
            icon: 'error'
        });
    } finally {
        loading.value = false;
    }
}

function applyFilters() {
    loadFireHistory();
}

function viewDetails(fire) {
    selectedFire.value = fire;
    detailsDialog.value = true;
}

onMounted(() => {
    loadFireHistory();
});
</script>

<style lang="scss" scoped>
.history-page {
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
  
  .filter-btn {
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

.stat-card {
  text-align: center;
  
  .stat-icon {
    margin-bottom: 1rem;
  }
  
  .text-h4 {
    font-weight: 700;
    margin-bottom: 0.5rem;
  }
  
  &:hover {
    .stat-icon {
      transform: scale(1.1);
      transition: transform 0.3s ease;
    }
  }
}

.chart-card {
  .card-content {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
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

    .region-progress {
      border-radius: 4px;
      margin-top: 8px;
    }
  }
}

.table-card {
  .history-table {
    border-radius: 12px;
    overflow: hidden;
    
    .q-table__top {
      background: transparent;
    }
    
    .q-table__bottom {
      background: transparent;
    }
  }
  
  .severity-badge {
    font-weight: 600;
    border-radius: 8px;
    padding: 4px 8px;
  }
  
  .action-btn {
    transition: all 0.2s ease;
    
    &:hover {
      background: rgba(37, 99, 235, 0.1);
      transform: scale(1.1);
    }
  }
}

.details-dialog {
  .detail-item {
    padding: 12px;
    border-radius: 8px;
    background: rgba(37, 99, 235, 0.05);
    transition: all 0.2s ease;
    
    &:hover {
      background: rgba(37, 99, 235, 0.1);
      transform: translateX(4px);
    }
  }
  
  .severity-badge {
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 16px;
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
  
  .stat-card {
    .stat-icon {
      .q-icon {
        font-size: 32px;
      }
    }
  }
}
</style>