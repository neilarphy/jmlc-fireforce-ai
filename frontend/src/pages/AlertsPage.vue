<template>
    <q-page class="alerts-page q-pa-lg">
        <!-- Заголовок страницы -->
        <div class="page-header q-mb-xl">
            <div class="text-h4 text-weight-bold text-primary">Оповещения</div>
            <div class="text-subtitle1 text-grey-6 q-mt-sm">Мониторинг и управление оповещениями о пожарах</div>
        </div>

        <div class="row q-col-gutter-xl">
            <!-- Header -->
            <div class="col-12">
                <q-card class="dashboard-card filters-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="notifications" size="28px" color="primary" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Система оповещений</div>
                                <div class="text-caption text-grey-6">Мониторинг и управление оповещениями</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <div class="row q-col-gutter-lg">
                            <div class="col-12 col-md-4">
                                <q-select outlined dense v-model="alertFilter" :options="alertFilterOptions"
                                    label="Фильтр оповещений" class="filter-input" />
                            </div>
                            <div class="col-12 col-md-4">
                                <q-select outlined dense v-model="regionFilter" :options="regionOptions"
                                    label="Регион" class="filter-input" />
                            </div>
                            <div class="col-12 col-md-4">
                                <q-btn-group spread class="action-buttons">
                                    <q-btn color="primary" icon="refresh" @click="refreshAlerts" :loading="loading" class="action-btn" />
                                    <q-btn color="secondary" icon="settings" @click="showSettings = true" class="action-btn" />
                                    <q-btn color="negative" icon="notifications_off" @click="muteAll" class="action-btn" />
                                </q-btn-group>
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>

            <!-- Alert Summary -->
            <div class="col-12">
                <div class="row q-col-gutter-lg">
                    <div class="col-12 col-md-3" v-for="(summary, index) in alertSummary" :key="index">
                        <q-card class="dashboard-card alert-summary-card" :class="getSummaryCardClass(summary)">
                            <q-card-section class="card-content text-center">
                                <div class="summary-icon q-mb-md">
                                    <q-icon :name="summary.icon" color="white" size="48px" />
                                </div>
                                <div class="text-h4 text-weight-bold text-white">{{ summary.count }}</div>
                                <div class="text-subtitle1 text-white opacity-9">{{ summary.label }}</div>
                            </q-card-section>
                        </q-card>
                    </div>
                </div>
            </div>

            <!-- Active Alerts -->
            <div class="col-12 col-lg-8">
                <q-card class="dashboard-card alerts-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="warning" size="28px" color="orange" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Активные оповещения</div>
                                <div class="text-caption text-grey-6">Текущие уведомления о пожарах</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <div v-if="filteredAlerts.length === 0" class="text-center q-py-xl">
                            <q-icon name="check_circle" color="positive" size="64px" class="q-mb-md" />
                            <div class="text-h6 text-grey-8 q-mb-md">Нет активных оповещений</div>
                            <div class="text-body2 text-grey-6">
                                Все системы работают нормально
                            </div>
                        </div>
                        <q-list separator v-else class="alerts-list">
                            <q-item v-for="alert in filteredAlerts" :key="alert.id" clickable
                                @click="viewAlertDetails(alert)" class="alert-item">
                                <q-item-section avatar>
                                    <q-avatar :color="getSeverityColor(alert.severity)" class="alert-avatar">
                                        <q-icon name="warning" color="white" />
                                    </q-avatar>
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">{{ alert.title }}</q-item-label>
                                    <q-item-label caption lines="2" class="text-grey-6">{{ alert.description }}</q-item-label>
                                    <div class="row items-center q-mt-sm">
                                        <q-badge :color="getSeverityColor(alert.severity)" class="severity-badge q-mr-sm">
                                            {{ alert.severity }}
                                        </q-badge>
                                        <q-icon name="place" size="xs" class="q-mr-xs" />
                                        <span class="text-caption text-grey-6">{{ alert.location }}</span>
                                        <q-space />
                                        <span class="text-caption text-grey-5">{{ alert.time }}</span>
                                    </div>
                                </q-item-section>
                                <q-item-section side>
                                    <div class="row items-center">
                                        <q-btn flat round dense icon="visibility" @click.stop="viewAlertDetails(alert)" class="action-btn" />
                                        <q-btn flat round dense icon="notifications_off" @click.stop="muteAlert(alert)" class="action-btn" />
                                    </div>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                </q-card>
            </div>

            <!-- Notification Settings -->
            <div class="col-12 col-lg-4">
                <q-card class="dashboard-card settings-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="settings" size="28px" color="blue" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Настройки уведомлений</div>
                                <div class="text-caption text-grey-6">Управление оповещениями</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-list separator class="settings-list">
                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">Критические оповещения</q-item-label>
                                    <q-item-label caption class="text-grey-6">Пожары с высоким риском для населения</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-toggle v-model="notificationSettings.critical" color="red" />
                                </q-item-section>
                            </q-item>
                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">Высокий риск</q-item-label>
                                    <q-item-label caption class="text-grey-6">Пожары с высокой вероятностью распространения</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-toggle v-model="notificationSettings.high" color="orange" />
                                </q-item-section>
                            </q-item>
                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">Средний риск</q-item-label>
                                    <q-item-label caption class="text-grey-6">Пожары среднего размера и интенсивности</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-toggle v-model="notificationSettings.medium" color="yellow" />
                                </q-item-section>
                            </q-item>
                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">Низкий риск</q-item-label>
                                    <q-item-label caption class="text-grey-6">Небольшие пожары с низким риском</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-toggle v-model="notificationSettings.low" color="green" />
                                </q-item-section>
                            </q-item>
                            <q-separator class="q-my-md" />
                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">Push-уведомления</q-item-label>
                                    <q-item-label caption class="text-grey-6">Уведомления в браузере</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-toggle v-model="notificationSettings.push" color="primary" />
                                </q-item-section>
                            </q-item>
                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">Email-уведомления</q-item-label>
                                    <q-item-label caption class="text-grey-6">Отправка на электронную почту</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-toggle v-model="notificationSettings.email" color="primary" />
                                </q-item-section>
                            </q-item>
                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">SMS-уведомления</q-item-label>
                                    <q-item-label caption class="text-grey-6">Отправка на мобильный телефон</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-toggle v-model="notificationSettings.sms" color="primary" />
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                    <q-card-actions align="right" class="card-content">
                        <q-btn flat label="Сбросить" color="grey" @click="resetSettings" />
                        <q-btn flat label="Сохранить" color="primary" @click="saveSettings" />
                    </q-card-actions>
                </q-card>
            </div>
        </div>

        <!-- Alert Details Dialog -->
        <q-dialog v-model="alertDetailsDialog" persistent>
            <q-card class="dashboard-card details-dialog" style="min-width: 400px; max-width: 600px">
                <q-card-section class="card-header">
                    <div class="row items-center">
                        <q-icon name="info" size="28px" color="primary" class="q-mr-md" />
                        <div class="text-h6 text-weight-bold">Детали оповещения</div>
                        <q-space />
                        <q-btn icon="close" flat round dense v-close-popup />
                    </div>
                </q-card-section>
                <q-card-section class="card-content" v-if="selectedAlert">
                    <div class="row q-col-gutter-md">
                        <div class="col-12">
                            <div class="text-h6">{{ selectedAlert.title }}</div>
                            <q-badge :color="getSeverityColor(selectedAlert.severity)" class="severity-badge q-mt-sm">
                                {{ selectedAlert.severity }}
                            </q-badge>
                        </div>
                        <div class="col-12">
                            <div class="text-caption text-grey-6">Описание</div>
                            <p class="text-body1">{{ selectedAlert.description }}</p>
                        </div>
                        <div class="col-12 col-md-6">
                            <div class="text-caption text-grey-6">Местоположение</div>
                            <p class="text-body1">{{ selectedAlert.location }}</p>
                        </div>
                        <div class="col-12 col-md-6">
                            <div class="text-caption text-grey-6">Время</div>
                            <p class="text-body1">{{ selectedAlert.time }}</p>
                        </div>
                        <div class="col-12">
                            <div class="text-caption text-grey-6">Рекомендуемые действия</div>
                            <q-list dense class="actions-list">
                                <q-item v-for="(action, index) in selectedAlert.actions" :key="index" class="action-item">
                                    <q-item-section avatar>
                                        <q-icon name="check_circle" color="green" />
                                    </q-item-section>
                                    <q-item-section>{{ action }}</q-item-section>
                                </q-item>
                            </q-list>
                        </div>
                    </div>
                </q-card-section>
                <q-card-actions align="right" class="card-content">
                    <q-btn flat label="Закрыть" color="primary" v-close-popup />
                    <q-btn flat label="Отметить как прочитанное" color="positive" @click="markAsRead" />
                </q-card-actions>
            </q-card>
        </q-dialog>

        <!-- Settings Dialog -->
        <q-dialog v-model="showSettings">
            <q-card class="dashboard-card settings-dialog" style="min-width: 400px">
                <q-card-section class="card-header">
                    <div class="row items-center">
                        <q-icon name="settings" size="28px" color="primary" class="q-mr-md" />
                        <div class="text-h6 text-weight-bold">Настройки оповещений</div>
                        <q-space />
                        <q-btn icon="close" flat round dense v-close-popup />
                    </div>
                </q-card-section>
                <q-card-section class="card-content">
                    <div class="text-subtitle2 q-mb-sm text-grey-6">Контактная информация</div>
                    <q-input outlined v-model="contactInfo.email" label="Email" class="q-mb-md contact-input" />
                    <q-input outlined v-model="contactInfo.phone" label="Телефон" class="q-mb-md contact-input" />
                    <div class="text-subtitle2 q-mb-sm q-mt-lg text-grey-6">Частота уведомлений</div>
                    <q-option-group v-model="contactInfo.frequency" :options="frequencyOptions" color="primary"
                        type="radio" />
                </q-card-section>
                <q-card-actions align="right" class="card-content">
                    <q-btn flat label="Отмена" color="grey" v-close-popup />
                    <q-btn flat label="Сохранить" color="primary" @click="saveContactInfo" />
                </q-card-actions>
            </q-card>
        </q-dialog>
    </q-page>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from 'src/boot/axios';
import { useQuasar } from 'quasar';

const $q = useQuasar();

const loading = ref(false);
const alertFilter = ref({ label: 'Все оповещения', value: 'all' });
const regionFilter = ref({ label: 'Все регионы', value: 'all' });
const alertDetailsDialog = ref(false);
const selectedAlert = ref(null);
const showSettings = ref(false);
const alerts = ref([]);
const alertSummary = ref([
    { label: 'Критические', count: 0, icon: 'warning', color: 'red' },
    { label: 'Высокий риск', count: 0, icon: 'priority_high', color: 'orange' },
    { label: 'Средний риск', count: 0, icon: 'info', color: 'yellow' },
    { label: 'Низкий риск', count: 0, icon: 'remove_circle', color: 'green' }
]);

const notificationSettings = ref({
    critical: true,
    high: true,
    medium: true,
    low: false,
    push: true,
    email: true,
    sms: false
});

const contactInfo = ref({
    email: 'user@example.com',
    phone: '+7 (999) 123-45-67',
    frequency: 'immediate'
});

const alertFilterOptions = [
    { label: 'Все оповещения', value: 'all' },
    { label: 'Критические', value: 'critical' },
    { label: 'Высокий риск', value: 'high' },
    { label: 'Средний риск', value: 'medium' },
    { label: 'Низкий риск', value: 'low' }
];

const regionOptions = [
    { label: 'Все регионы', value: 'all' },
    { label: 'Красноярский край', value: 'krasnoyarsk' },
    { label: 'Иркутская область', value: 'irkutsk' },
    { label: 'Республика Саха (Якутия)', value: 'yakutia' },
    { label: 'Забайкальский край', value: 'zabaykalsky' },
    { label: 'Амурская область', value: 'amur' }
];

const frequencyOptions = [
    { label: 'Немедленно', value: 'immediate' },
    { label: 'Раз в час', value: 'hourly' },
    { label: 'Раз в день', value: 'daily' },
    { label: 'Раз в неделю', value: 'weekly' }
];

const filteredAlerts = computed(() => {
    let result = alerts.value;

    if (alertFilter.value.value !== 'all') {
        result = result.filter(alert => alert.severity === alertFilter.value.value);
    }

    if (regionFilter.value.value !== 'all') {
        result = result.filter(alert => alert.location.toLowerCase().includes(regionFilter.value.label.toLowerCase()));
    }

    return result;
});

function getSeverityColor(severity) {
    switch (severity) {
        case 'critical': return 'red';
        case 'high': return 'orange';
        case 'medium': return 'yellow';
        case 'low': return 'green';
        default: return 'grey';
    }
}

function getSummaryCardClass(summary) {
    switch (summary.color) {
        case 'red': return 'bg-critical';
        case 'orange': return 'bg-high';
        case 'yellow': return 'bg-medium';
        case 'green': return 'bg-low';
        default: return '';
    }
}

async function loadAlerts() {
    loading.value = true;
    try {
        // Временно используем мок-данные вместо API
        const mockAlerts = [
            {
                id: 1,
                title: 'Критический пожар в Красноярском крае',
                description: 'Обнаружен крупный пожар в районе Красноярска',
                severity: 'critical',
                region: 'Красноярский край',
                timestamp: '2024-01-15 14:30:00',
                status: 'active'
            },
            {
                id: 2,
                title: 'Высокий риск в Иркутской области',
                description: 'Повышенная пожарная опасность в регионе',
                severity: 'high',
                region: 'Иркутская область',
                timestamp: '2024-01-15 13:15:00',
                status: 'active'
            },
            {
                id: 3,
                title: 'Средний риск в Республике Саха',
                description: 'Умеренная пожарная опасность',
                severity: 'medium',
                region: 'Республика Саха',
                timestamp: '2024-01-15 12:45:00',
                status: 'active'
            }
        ];

        const mockSummary = {
            critical: 1,
            high: 1,
            medium: 1,
            low: 0
        };

        alerts.value = mockAlerts;

        alertSummary.value = [
            { label: 'Критические', count: mockSummary.critical, icon: 'warning', color: 'red' },
            { label: 'Высокий риск', count: mockSummary.high, icon: 'priority_high', color: 'orange' },
            { label: 'Средний риск', count: mockSummary.medium, icon: 'info', color: 'yellow' },
            { label: 'Низкий риск', count: mockSummary.low, icon: 'remove_circle', color: 'green' }
        ];
    } catch (error) {
        console.error('Error loading alerts:', error);
        $q.notify({
            color: 'negative',
            message: 'Ошибка загрузки оповещений',
            icon: 'error'
        });
    } finally {
        loading.value = false;
    }
}

function refreshAlerts() {
    loadAlerts();
    $q.notify({
        color: 'positive',
        message: 'Оповещения обновлены',
        icon: 'update'
    });
}

function viewAlertDetails(alert) {
    selectedAlert.value = alert;
    alertDetailsDialog.value = true;
}

function muteAlert(alert) {
    $q.dialog({
        title: 'Отключить оповещения',
        message: `Вы уверены, что хотите отключить оповещения о "${alert.title}"?`,
        cancel: true,
        persistent: true
    }).onOk(() => {
        alerts.value = alerts.value.filter(a => a.id !== alert.id);
        $q.notify({
            color: 'positive',
            message: 'Оповещение отключено',
            icon: 'notifications_off'
        });
    });
}

function muteAll() {
    $q.dialog({
        title: 'Отключить все оповещения',
        message: 'Вы уверены, что хотите отключить все активные оповещения?',
        cancel: true,
        persistent: true
    }).onOk(() => {
        alerts.value = [];
        $q.notify({
            color: 'positive',
            message: 'Все оповещения отключены',
            icon: 'notifications_off'
        });
    });
}

function markAsRead() {
    alertDetailsDialog.value = false;
    $q.notify({
        color: 'positive',
        message: 'Оповещение отмечено как прочитанное',
        icon: 'check'
    });
}

function resetSettings() {
    notificationSettings.value = {
        critical: true,
        high: true,
        medium: true,
        low: false,
        push: true,
        email: true,
        sms: false
    };
}

async function saveSettings() {
    try {
        await api.put('/api/user/settings', {
            notifications: notificationSettings.value
        });

        $q.notify({
            color: 'positive',
            message: 'Настройки сохранены',
            icon: 'check'
        });
    } catch (error) {
        console.error('Error saving settings:', error);
        $q.notify({
            color: 'negative',
            message: 'Ошибка сохранения настроек',
            icon: 'error'
        });
    }
}

function saveContactInfo() {
    showSettings.value = false;
    $q.notify({
        color: 'positive',
        message: 'Контактная информация сохранена',
        icon: 'check'
    });
}

onMounted(() => {
    loadAlerts();
});
</script>

<style lang="scss" scoped>
.alerts-page {
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
  
  .action-buttons {
    .action-btn {
      border-radius: 12px;
      transition: all 0.2s ease;
      
      &:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      }
    }
  }
}

.alert-summary-card {
  text-align: center;
  
  .summary-icon {
    margin-bottom: 1rem;
    transition: transform 0.3s ease;
  }
  
  &:hover {
    .summary-icon {
      transform: scale(1.1);
    }
  }
}

.bg-critical {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3);
}

.bg-high {
  background: linear-gradient(135deg, #f97316, #ea580c);
  box-shadow: 0 8px 32px rgba(249, 115, 22, 0.3);
}

.bg-medium {
  background: linear-gradient(135deg, #eab308, #ca8a04);
  box-shadow: 0 8px 32px rgba(234, 179, 8, 0.3);
}

.bg-low {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  box-shadow: 0 8px 32px rgba(34, 197, 94, 0.3);
}

.alerts-card {
  .alerts-list {
    .alert-item {
      border-radius: 12px;
      margin: 8px 0;
      padding: 16px;
      transition: all 0.2s ease;
      border: 1px solid transparent;

      &:hover {
        background: rgba(37, 99, 235, 0.05);
        border-color: rgba(37, 99, 235, 0.1);
        transform: translateX(4px);
      }
    }

    .alert-avatar {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
}

.settings-card {
  .settings-list {
    .setting-item {
      border-radius: 12px;
      margin: 8px 0;
      padding: 16px;
      transition: all 0.2s ease;
      border: 1px solid transparent;

      &:hover {
        background: rgba(37, 99, 235, 0.05);
        border-color: rgba(37, 99, 235, 0.1);
        transform: translateX(4px);
      }
    }
  }
}

.details-dialog {
  .actions-list {
    .action-item {
      border-radius: 8px;
      margin: 4px 0;
      padding: 8px;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba(37, 99, 235, 0.05);
        transform: translateX(2px);
      }
    }
  }
  
  .severity-badge {
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 16px;
  }
}

.settings-dialog {
  .contact-input {
    border-radius: 12px;
    
    .q-field__control {
      border-radius: 12px;
    }
  }
}

.opacity-9 {
  opacity: 0.9;
}

// Responsive adjustments
@media (max-width: 768px) {
  .page-header {
    padding: 1rem 0;
    
    .text-h4 {
      font-size: 1.75rem;
    }
  }
  
  .alert-summary-card {
    .summary-icon {
      .q-icon {
        font-size: 32px;
      }
    }
  }
}
</style>