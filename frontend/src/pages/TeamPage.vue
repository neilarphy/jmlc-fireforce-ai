<template>
    <q-page class="team-page q-pa-lg">
        <!-- Заголовок страницы -->
        <div class="page-header q-mb-xl">
            <div class="text-h4 text-weight-bold text-primary">Команда</div>
            <div class="text-subtitle1 text-grey-6 q-mt-sm">Совместный мониторинг и управление пожарной безопасностью</div>
        </div>

        <div class="row q-col-gutter-xl">
            <!-- Header -->
            <div class="col-12">
                <q-card class="dashboard-card team-header-card">
                    <q-card-section class="card-content">
                        <div class="row items-center">
                            <div class="col">
                                <div class="text-h5 text-weight-bold text-white">Командный центр</div>
                                <p class="text-white q-mt-xs opacity-80">Совместный мониторинг и управление пожарной
                                    безопасностью</p>
                            </div>
                            <div class="col-auto">
                                <q-btn color="white" text-color="primary" label="Настроить команду" icon="settings"
                                    @click="showTeamSettings = true" class="header-btn" />
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>

            <!-- Team Stats -->
            <div class="col-12">
                <div class="row q-col-gutter-lg">
                    <div class="col-12 col-md-3" v-for="(stat, index) in teamStats" :key="index">
                        <q-card class="dashboard-card stat-card">
                            <q-card-section class="card-content text-center">
                                <div class="stat-icon q-mb-md">
                                    <q-icon :name="stat.icon" :color="stat.color" size="48px" />
                                </div>
                                <div class="text-h4 text-weight-bold" :class="`text-${stat.color}`">{{
                                    stat.value }}</div>
                                <div class="text-subtitle1 text-grey-6">{{ stat.label }}</div>
                                <div class="text-caption text-grey-5">{{ stat.description }}</div>
                            </q-card-section>
                        </q-card>
                    </div>
                </div>
            </div>

            <!-- Active Team Members -->
            <div class="col-12 col-lg-8">
                <q-card class="dashboard-card members-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="people" size="28px" color="blue" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Активные участники</div>
                                <div class="text-caption text-grey-6">Текущий статус команды мониторинга</div>
                            </div>
                            <q-space />
                            <q-btn flat color="primary" icon="person_add" label="Добавить"
                                @click="showAddMember = true" class="add-member-btn" />
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-list separator class="members-list">
                            <q-item v-for="member in activeMembers" :key="member.id" class="member-item">
                                <q-item-section avatar>
                                    <q-avatar :color="member.status === 'online' ? 'positive' : 'grey'"
                                        text-color="white" class="member-avatar">
                                        {{ member.initials }}
                                        <q-badge v-if="member.status === 'online'" floating color="positive" rounded />
                                    </q-avatar>
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">{{ member.name }}</q-item-label>
                                    <q-item-label caption class="text-grey-6">{{ member.role }} • {{ member.location }}</q-item-label>
                                    <div class="row items-center q-mt-sm">
                                        <q-chip :color="member.status === 'online' ? 'positive' : 'grey'"
                                            text-color="white" size="sm" class="status-chip">
                                            {{ member.status === 'online' ? 'В сети' : 'Не в сети' }}
                                        </q-chip>
                                        <q-chip v-if="member.currentTask" color="blue" text-color="white" size="sm"
                                            class="task-chip q-ml-xs">
                                            {{ member.currentTask }}
                                        </q-chip>
                                    </div>
                                </q-item-section>
                                <q-item-section side>
                                    <div class="row items-center">
                                        <q-btn flat round dense icon="message" color="primary"
                                            @click="contactMember(member)" class="action-btn" />
                                        <q-btn flat round dense icon="more_vert" color="grey" class="action-btn">
                                            <q-menu>
                                                <q-list>
                                                    <q-item clickable @click="viewMemberDetails(member)">
                                                        <q-item-section>Подробности</q-item-section>
                                                    </q-item>
                                                    <q-item clickable @click="assignTask(member)">
                                                        <q-item-section>Назначить задачу</q-item-section>
                                                    </q-item>
                                                </q-list>
                                            </q-menu>
                                        </q-btn>
                                    </div>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                </q-card>
            </div>

            <!-- Team Activity & Reports -->
            <div class="col-12 col-lg-4">
                <q-card class="dashboard-card activity-card q-mb-lg">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="timeline" size="28px" color="orange" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Последняя активность</div>
                                <div class="text-caption text-grey-6">Недавние события команды</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-list separator class="activity-list">
                            <q-item v-for="activity in recentActivity" :key="activity.id" class="activity-item">
                                <q-item-section avatar>
                                    <q-avatar
                                        :color="activity.type === 'alert' ? 'negative' : activity.type === 'report' ? 'blue' : 'positive'"
                                        size="32px" class="activity-avatar">
                                        <q-icon :name="activity.icon" color="white" size="16px" />
                                    </q-avatar>
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium">{{ activity.title }}</q-item-label>
                                    <q-item-label caption class="text-grey-6">{{ activity.user }} • {{ activity.time }}</q-item-label>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                </q-card>

                <q-card class="dashboard-card reports-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="assessment" size="28px" color="green" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Быстрые отчеты</div>
                                <div class="text-caption text-grey-6">Генерация отчетов</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <div class="row q-col-gutter-sm">
                            <div class="col-6" v-for="report in quickReports" :key="report.id">
                                <q-btn :color="report.color" :icon="report.icon" :label="report.label"
                                    class="full-width report-btn" size="sm" @click="generateReport(report)" />
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>

            <!-- Shared Workspace -->
            <div class="col-12">
                <q-card class="dashboard-card workspace-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="work" size="28px" color="purple" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Общее рабочее пространство</div>
                                <div class="text-caption text-grey-6">Совместные документы и ресурсы команды</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-tabs v-model="workspaceTab" class="text-grey workspace-tabs" active-color="primary" indicator-color="primary"
                            align="left">
                            <q-tab name="documents" label="Документы" icon="description" />
                            <q-tab name="maps" label="Карты" icon="map" />
                            <q-tab name="protocols" label="Протоколы" icon="rule" />
                            <q-tab name="contacts" label="Контакты" icon="contacts" />
                        </q-tabs>
                        <q-separator class="q-my-md" />
                        <q-tab-panels v-model="workspaceTab" animated>
                            <q-tab-panel name="documents">
                                <div class="row q-col-gutter-lg">
                                    <div class="col-12 col-md-6 col-lg-4" v-for="doc in sharedDocuments" :key="doc.id">
                                        <q-card class="dashboard-card document-card" clickable @click="openDocument(doc)">
                                            <q-card-section class="card-content">
                                                <div class="row items-center">
                                                    <q-icon :name="doc.icon" :color="doc.color" size="24px" />
                                                    <div class="q-ml-sm">
                                                        <div class="text-weight-medium">{{ doc.name }}</div>
                                                        <div class="text-caption text-grey-6">{{ doc.lastModified }}</div>
                                                    </div>
                                                </div>
                                            </q-card-section>
                                        </q-card>
                                    </div>
                                </div>
                            </q-tab-panel>
                            <q-tab-panel name="maps">
                                <div class="text-center text-grey q-py-xl">
                                    <q-icon name="map" size="64px" class="q-mb-md" />
                                    <div class="text-h6 q-mt-md">Общие карты</div>
                                    <div class="text-body2">Здесь будут отображаться совместные карты команды</div>
                                </div>
                            </q-tab-panel>
                            <q-tab-panel name="protocols">
                                <div class="text-center text-grey q-py-xl">
                                    <q-icon name="rule" size="64px" class="q-mb-md" />
                                    <div class="text-h6 q-mt-md">Протоколы действий</div>
                                    <div class="text-body2">Стандартные процедуры и протоколы реагирования</div>
                                </div>
                            </q-tab-panel>
                            <q-tab-panel name="contacts">
                                <div class="text-center text-grey q-py-xl">
                                    <q-icon name="contacts" size="64px" class="q-mb-md" />
                                    <div class="text-h6 q-mt-md">Экстренные контакты</div>
                                    <div class="text-body2">Список важных контактов и служб</div>
                                </div>
                            </q-tab-panel>
                        </q-tab-panels>
                    </q-card-section>
                </q-card>
            </div>
        </div>

        <!-- Team Settings Dialog -->
        <q-dialog v-model="showTeamSettings" persistent>
            <q-card class="dashboard-card settings-dialog" style="min-width: 400px">
                <q-card-section class="card-header">
                    <div class="row items-center">
                        <q-icon name="settings" size="28px" color="primary" class="q-mr-md" />
                        <div class="text-h6 text-weight-bold">Настройки команды</div>
                        <q-space />
                        <q-btn icon="close" flat round dense v-close-popup />
                    </div>
                </q-card-section>
                <q-card-section class="card-content">
                    <q-input outlined v-model="teamSettings.name" label="Название команды" class="q-mb-md settings-input" />
                    <q-input outlined v-model="teamSettings.description" label="Описание" type="textarea"
                        class="q-mb-md settings-input" />
                    <q-select outlined v-model="teamSettings.timezone" :options="timezoneOptions"
                        label="Часовой пояс" class="settings-input" />
                </q-card-section>
                <q-card-actions align="right" class="card-content">
                    <q-btn flat label="Отмена" color="grey" v-close-popup />
                    <q-btn flat label="Сохранить" color="primary" @click="saveTeamSettings" />
                </q-card-actions>
            </q-card>
        </q-dialog>

        <!-- Add Member Dialog -->
        <q-dialog v-model="showAddMember" persistent>
            <q-card class="dashboard-card member-dialog" style="min-width: 400px">
                <q-card-section class="card-header">
                    <div class="row items-center">
                        <q-icon name="person_add" size="28px" color="primary" class="q-mr-md" />
                        <div class="text-h6 text-weight-bold">Добавить участника</div>
                        <q-space />
                        <q-btn icon="close" flat round dense v-close-popup />
                    </div>
                </q-card-section>
                <q-card-section class="card-content">
                    <q-input outlined v-model="newMember.name" label="Имя" class="q-mb-md member-input" />
                    <q-input outlined v-model="newMember.email" label="Email" class="q-mb-md member-input" />
                    <q-select outlined v-model="newMember.role" :options="roleOptions" label="Роль" class="member-input" />
                </q-card-section>
                <q-card-actions align="right" class="card-content">
                    <q-btn flat label="Отмена" color="grey" v-close-popup />
                    <q-btn flat label="Добавить" color="primary" @click="addMember" />
                </q-card-actions>
            </q-card>
        </q-dialog>
    </q-page>
</template>

<script setup>
import { ref } from 'vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();

const showTeamSettings = ref(false);
const showAddMember = ref(false);
const workspaceTab = ref('documents');

const teamStats = ref([
    { label: 'Активных участников', value: '12', icon: 'people', color: 'positive', description: 'Сейчас в сети' },
    { label: 'Активных задач', value: '8', icon: 'assignment', color: 'blue', description: 'В работе' },
    { label: 'Критических событий', value: '3', icon: 'warning', color: 'negative', description: 'Требуют внимания' },
    { label: 'Готовность команды', value: '94%', icon: 'shield', color: 'orange', description: 'Общий показатель' }
]);

const activeMembers = ref([
    {
        id: 1,
        name: 'Алексей Иванов',
        role: 'Руководитель смены',
        initials: 'АИ',
        status: 'online',
        location: 'Москва',
        currentTask: 'Мониторинг МО'
    },
    {
        id: 2,
        name: 'Мария Петрова',
        role: 'Аналитик данных',
        initials: 'МП',
        status: 'online',
        location: 'СПб',
        currentTask: 'Анализ рисков'
    },
    {
        id: 3,
        name: 'Дмитрий Сидоров',
        role: 'Оператор',
        initials: 'ДС',
        status: 'offline',
        location: 'Екатеринбург',
        currentTask: null
    },
    {
        id: 4,
        name: 'Елена Козлова',
        role: 'Координатор',
        initials: 'ЕК',
        status: 'online',
        location: 'Новосибирск',
        currentTask: 'Координация'
    }
]);

const recentActivity = ref([
    { id: 1, title: 'Критическое оповещение', user: 'Алексей И.', time: '5 мин назад', type: 'alert', icon: 'warning' },
    { id: 2, title: 'Отчет создан', user: 'Мария П.', time: '15 мин назад', type: 'report', icon: 'description' },
    { id: 3, title: 'Задача выполнена', user: 'Елена К.', time: '30 мин назад', type: 'task', icon: 'check_circle' },
    { id: 4, title: 'Новый участник', user: 'Система', time: '1 час назад', type: 'user', icon: 'person_add' }
]);

const quickReports = ref([
    { id: 1, label: 'Сводка дня', icon: 'today', color: 'primary' },
    { id: 2, label: 'Статус команды', icon: 'people', color: 'positive' },
    { id: 3, label: 'Критические события', icon: 'warning', color: 'negative' },
    { id: 4, label: 'Производительность', icon: 'trending_up', color: 'blue' }
]);

const sharedDocuments = ref([
    { id: 1, name: 'Протокол действий при пожаре', icon: 'description', color: 'red', lastModified: '2 дня назад' },
    { id: 2, name: 'Контакты экстренных служб', icon: 'contacts', color: 'blue', lastModified: '1 неделю назад' },
    { id: 3, name: 'Инструкция по эвакуации', icon: 'exit_to_app', color: 'orange', lastModified: '3 дня назад' },
    { id: 4, name: 'Отчет за месяц', icon: 'assessment', color: 'green', lastModified: 'Вчера' }
]);

const teamSettings = ref({
    name: 'Центр мониторинга пожаров',
    description: 'Команда по мониторингу и предотвращению пожаров в Центральном регионе',
    timezone: 'Europe/Moscow'
});

const newMember = ref({
    name: '',
    email: '',
    role: ''
});

const timezoneOptions = [
    'Europe/Moscow',
    'Europe/Kaliningrad',
    'Asia/Yekaterinburg',
    'Asia/Novosibirsk',
    'Asia/Krasnoyarsk',
    'Asia/Irkutsk',
    'Asia/Yakutsk',
    'Asia/Vladivostok'
];

const roleOptions = [
    'Руководитель смены',
    'Аналитик данных',
    'Оператор',
    'Координатор',
    'Специалист по безопасности'
];

function contactMember(member) {
    $q.notify({
        color: 'info',
        message: `Отправлено сообщение для ${member.name}`,
        icon: 'message',
        timeout: 2000
    });
}

function viewMemberDetails(member) {
    $q.notify({
        color: 'info',
        message: `Просмотр деталей: ${member.name}`,
        icon: 'visibility',
        timeout: 2000
    });
}

function assignTask(member) {
    $q.notify({
        color: 'positive',
        message: `Назначена задача для ${member.name}`,
        icon: 'assignment',
        timeout: 2000
    });
}

function generateReport(report) {
    $q.notify({
        color: 'positive',
        message: `Генерируется отчет: ${report.label}`,
        icon: report.icon,
        timeout: 2000
    });
}

function openDocument(doc) {
    $q.notify({
        color: 'info',
        message: `Открывается документ: ${doc.name}`,
        icon: 'open_in_new',
        timeout: 2000
    });
}

function saveTeamSettings() {
    showTeamSettings.value = false;
    $q.notify({
        color: 'positive',
        message: 'Настройки команды сохранены',
        icon: 'check',
        timeout: 2000
    });
}

function addMember() {
    if (newMember.value.name && newMember.value.email && newMember.value.role) {
        activeMembers.value.push({
            id: Date.now(),
            name: newMember.value.name,
            role: newMember.value.role,
            initials: newMember.value.name.split(' ').map(n => n[0]).join(''),
            status: 'offline',
            location: 'Не указано',
            currentTask: null
        });

        newMember.value = { name: '', email: '', role: '' };
        showAddMember.value = false;

        $q.notify({
            color: 'positive',
            message: 'Участник добавлен в команду',
            icon: 'person_add',
            timeout: 2000
        });
    }
}
</script>

<style lang="scss" scoped>
.team-page {
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

.team-header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  .header-btn {
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(255, 255, 255, 0.3);
    }
  }
}

.stat-card {
  text-align: center;
  
  .stat-icon {
    margin-bottom: 1rem;
    transition: transform 0.3s ease;
  }
  
  .text-h4 {
    font-weight: 700;
    margin-bottom: 0.5rem;
  }
  
  &:hover {
    .stat-icon {
      transform: scale(1.1);
    }
  }
}

.members-card {
  .members-list {
    .member-item {
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

    .member-avatar {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .status-chip {
      font-weight: 600;
      border-radius: 8px;
    }

    .task-chip {
      font-weight: 600;
      border-radius: 8px;
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

.activity-card {
  .activity-list {
    .activity-item {
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

    .activity-avatar {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
  }
}

.reports-card {
  .report-btn {
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
  }
}

.workspace-card {
  .workspace-tabs {
    .q-tab {
      border-radius: 8px;
      margin-right: 8px;
      transition: all 0.2s ease;
      
      &:hover {
        background: rgba(37, 99, 235, 0.1);
      }
    }
  }
  
  .document-card {
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }
  }
}

.settings-dialog {
  .settings-input {
    border-radius: 12px;
    
    .q-field__control {
      border-radius: 12px;
    }
  }
}

.member-dialog {
  .member-input {
    border-radius: 12px;
    
    .q-field__control {
      border-radius: 12px;
    }
  }
}

.add-member-btn {
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  }
}

.opacity-80 {
  opacity: 0.8;
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