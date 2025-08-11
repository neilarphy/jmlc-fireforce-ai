<template>
    <q-page class="settings-page q-pa-lg">
        <!-- Заголовок страницы -->
        <div class="page-header q-mb-xl">
            <div class="text-h4 text-weight-bold text-primary">Настройки</div>
            <div class="text-subtitle1 text-grey-6 q-mt-sm">Управление параметрами приложения</div>
        </div>

        <div class="row q-col-gutter-xl justify-center">
            <!-- Appearance Settings -->
            <div class="col-12 col-lg-5">
                <q-card class="settings-card equal-height">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="palette" size="28px" color="purple" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Внешний вид</div>
                                <div class="text-caption text-grey-6">Настройки отображения интерфейса</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-list class="settings-list">
                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section avatar>
                                    <q-icon :name="themeStore.isDark ? 'dark_mode' : 'light_mode'"
                                        :color="themeStore.isDark ? 'amber' : 'blue'" size="24px" />
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium text-body1">Темная тема</q-item-label>
                                    <q-item-label caption class="text-caption">Переключить на темную тему интерфейса</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-toggle v-model="settings.darkMode" color="primary" size="lg"
                                        @update:model-value="toggleTheme" />
                                </q-item-section>
                            </q-item>

                            <q-separator class="q-my-md" />

                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section avatar>
                                    <q-icon name="palette" color="purple" size="24px" />
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium text-body1">Цветовая схема</q-item-label>
                                    <q-item-label caption class="text-caption">Выберите основные цвета интерфейса</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-select v-model="settings.colorScheme" :options="colorSchemeOptions" outlined
                                        dense class="color-select" @update:model-value="updateColorScheme" />
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                </q-card>
            </div>

            <!-- System Settings -->
            <div class="col-12 col-lg-5">
                <q-card class="settings-card equal-height">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="settings" size="28px" color="blue" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Система</div>
                                <div class="text-caption text-grey-6">Настройки работы приложения</div>
                            </div>
                        </div>
                    </q-card-section>
                    <q-card-section class="card-content">
                        <q-list class="settings-list">
                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section avatar>
                                    <q-icon name="refresh" color="green" size="24px" />
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium text-body1">Автообновление данных</q-item-label>
                                    <q-item-label caption class="text-caption">Автоматически обновлять данные каждые 5 минут</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-toggle v-model="settings.autoRefresh" color="primary" size="lg" />
                                </q-item-section>
                            </q-item>

                            <q-separator class="q-my-md" />

                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section avatar>
                                    <q-icon name="volume_up" color="orange" size="24px" />
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium text-body1">Звуковые уведомления</q-item-label>
                                    <q-item-label caption class="text-caption">Воспроизводить звук при получении уведомлений</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-toggle v-model="settings.soundNotifications" color="primary" size="lg" />
                                </q-item-section>
                            </q-item>

                            <q-separator class="q-my-md" />

                            <q-item tag="label" v-ripple class="setting-item">
                                <q-item-section avatar>
                                    <q-icon name="language" color="blue" size="24px" />
                                </q-item-section>
                                <q-item-section>
                                    <q-item-label class="text-weight-medium text-body1">Язык интерфейса</q-item-label>
                                    <q-item-label caption class="text-caption">Выберите язык отображения</q-item-label>
                                </q-item-section>
                                <q-item-section side>
                                    <q-select v-model="settings.language" :options="languageOptions" outlined dense
                                        class="language-select" />
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                </q-card>
            </div>

            <!-- Notification Settings (Mock) -->
            <div class="col-12 col-lg-10">
                <q-card class="settings-card">
                    <q-card-section class="card-header">
                        <div class="row items-center">
                            <q-icon name="notifications" size="28px" color="orange" class="q-mr-md" />
                            <div>
                                <div class="text-h6 text-weight-bold">Уведомления</div>
                                <div class="text-caption text-grey-6">Подключение Telegram и уведомления на email (мок)</div>
                            </div>
                        </div>
                    </q-card-section>

                    <q-card-section class="card-content">
                        <div class="row q-col-gutter-xl">
                            <!-- Email notifications -->
                            <div class="col-12 col-md-6">
                                <div class="text-subtitle2 text-weight-bold q-mb-md">Email</div>
                                <q-list class="settings-list">
                                    <q-item class="setting-item">
                                        <q-item-section avatar>
                                            <q-icon name="email" color="primary" />
                                        </q-item-section>
                                        <q-item-section>
                                            <q-item-label class="text-weight-medium text-body1">Email для уведомлений</q-item-label>
                                            <q-item-label caption class="text-caption">На этот адрес будут отправляться уведомления</q-item-label>
                                        </q-item-section>
                                        <q-item-section side class="full-width-input">
                                            <q-input v-model="notificationSettings.email" type="email" outlined dense placeholder="name@example.com" />
                                        </q-item-section>
                                    </q-item>

                                    <q-item tag="label" v-ripple class="setting-item">
                                        <q-item-section avatar>
                                            <q-icon name="mark_email_read" color="green" />
                                        </q-item-section>
                                        <q-item-section>
                                            <q-item-label class="text-weight-medium text-body1">Включить email-уведомления</q-item-label>
                                            <q-item-label caption class="text-caption">Получать предупреждения и отчеты на почту</q-item-label>
                                        </q-item-section>
                                        <q-item-section side>
                                            <q-toggle v-model="notificationSettings.emailEnabled" color="primary" size="lg" />
                                        </q-item-section>
                                    </q-item>

                                    <div class="row items-center q-mt-md">
                                        <q-btn color="primary" icon="outgoing_mail" label="Отправить тестовое письмо" @click="sendTestEmail" class="q-mr-sm" />
                                    </div>
                                </q-list>
                            </div>

                            <!-- Telegram notifications -->
                            <div class="col-12 col-md-6">
                                <div class="text-subtitle2 text-weight-bold q-mb-md">Telegram</div>
                                <q-list class="settings-list">
                                    <q-item class="setting-item">
                                        <q-item-section avatar>
                                            <q-icon name="telegram" color="blue" />
                                        </q-item-section>
                                        <q-item-section>
                                            <q-item-label class="text-weight-medium text-body1">Подключение Telegram</q-item-label>
                                            <q-item-label caption class="text-caption">
                                                {{ telegramConnection.connected ? `Подключено как @${notificationSettings.telegramUsername}` : 'Подключите аккаунт Telegram для получения уведомлений' }}
                                            </q-item-label>
                                        </q-item-section>
                                        <q-item-section side>
                                            <q-btn v-if="!telegramConnection.connected" color="primary" outline icon="link" label="Подключить" @click="startTelegramConnection" />
                                            <q-btn v-else color="negative" outline icon="link_off" label="Отключить" @click="disconnectTelegram" />
                                        </q-item-section>
                                    </q-item>

                                    <q-item class="setting-item">
                                        <q-item-section avatar>
                                            <q-icon name="person" color="purple" />
                                        </q-item-section>
                                        <q-item-section>
                                            <q-item-label class="text-weight-medium text-body1">Telegram username</q-item-label>
                                            <q-item-label caption class="text-caption">Укажите ваш @username</q-item-label>
                                        </q-item-section>
                                        <q-item-section side class="full-width-input">
                                            <q-input v-model="notificationSettings.telegramUsername" :disable="!telegramConnection.connected" prefix="@" outlined dense placeholder="username" />
                                        </q-item-section>
                                    </q-item>

                                    <q-item tag="label" v-ripple class="setting-item">
                                        <q-item-section avatar>
                                            <q-icon name="notifications_active" color="orange" />
                                        </q-item-section>
                                        <q-item-section>
                                            <q-item-label class="text-weight-medium text-body1">Уведомления в Telegram</q-item-label>
                                            <q-item-label caption class="text-caption">Получать предупреждения и отчеты в Telegram</q-item-label>
                                        </q-item-section>
                                        <q-item-section side>
                                            <q-toggle v-model="notificationSettings.telegramEnabled" :disable="!telegramConnection.connected" color="primary" size="lg" />
                                        </q-item-section>
                                    </q-item>

                                    <div class="row items-center q-mt-md">
                                        <q-btn color="primary" icon="send" label="Отправить тестовое сообщение" @click="sendTestTelegram" :disable="!telegramConnection.connected" />
                                    </div>
                                </q-list>
                            </div>
                        </div>
                    </q-card-section>
                </q-card>
            </div>
        </div>

        <!-- Save Button -->
        <div class="fixed-bottom-right q-pa-lg">
            <q-btn fab color="primary" icon="save" @click="saveSettings" class="save-btn shadow-up-12">
                <q-tooltip>Сохранить настройки</q-tooltip>
            </q-btn>
        </div>

        <!-- Telegram connect dialog (Mock) -->
        <q-dialog v-model="telegramDialog.visible">
            <q-card style="min-width: 420px">
                <q-card-section class="row items-center q-pb-none">
                    <div class="text-h6">Подключение Telegram (мок)</div>
                    <q-space />
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-card-section>
                <q-card-section>
                    <div class="q-mb-md">
                        1) Откройте Telegram и начните чат с ботом <span class="text-weight-bold">@FireForceAIBot</span> (демо).<br>
                        2) Отправьте боту команду <span class="text-weight-bold">/start</span> и код подключения:<br>
                    </div>
                    <div class="bg-grey-2 text-center q-pa-md q-mb-md" style="border-radius: 12px;">
                        <div class="text-caption text-grey-7 q-mb-xs">Код подключения</div>
                        <div class="text-h5 text-weight-bold">{{ telegramDialog.code }}</div>
                    </div>
                    <div class="q-mb-md">
                        3) После отправки кода нажмите «Подтвердить» ниже. Это демонстрация — соединение будет считаться установленным.
                    </div>
                </q-card-section>
                <q-card-actions align="right">
                    <q-btn flat label="Отмена" v-close-popup />
                    <q-btn color="primary" label="Подтвердить" @click="confirmTelegramConnection" />
                </q-card-actions>
            </q-card>
        </q-dialog>
    </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useThemeStore } from 'src/stores/theme';
import { applyColorScheme } from 'src/utils/colorScheme';

const $q = useQuasar();
const themeStore = useThemeStore();

const settings = ref({
    darkMode: false,
    autoRefresh: true,
    soundNotifications: true,
    language: { label: 'Русский', value: 'ru' },
    colorScheme: { label: 'Синяя', value: 'blue' }
});

// Mock notification settings state
const notificationSettings = ref({
    email: '',
    emailEnabled: false,
    telegramUsername: '',
    telegramEnabled: false
});

const telegramConnection = ref({
    connected: false
});

const telegramDialog = ref({
    visible: false,
    code: ''
});

const colorSchemeOptions = [
    { label: 'Синяя', value: 'blue' },
    { label: 'Красная', value: 'red' },
    { label: 'Зеленая', value: 'green' },
    { label: 'Оранжевая', value: 'orange' },
    { label: 'Фиолетовая', value: 'purple' }
];

const languageOptions = [
    { label: 'Русский', value: 'ru' },
    { label: 'English', value: 'en' }
];

function toggleTheme() {
    themeStore.setTheme(settings.value.darkMode);
}

function updateColorScheme() {
    applyColorScheme(settings.value.colorScheme.value);
    
    // Сохраняем выбранную схему в localStorage
    localStorage.setItem('colorScheme', JSON.stringify(settings.value.colorScheme));
    
    $q.notify({
        color: 'positive',
        message: `Цветовая схема изменена на "${settings.value.colorScheme.label}"`,
        icon: 'palette',
        timeout: 2000
    });
}

function saveSettings() {
    try {
        // Сохраняем настройки в localStorage
        localStorage.setItem('colorScheme', JSON.stringify(settings.value.colorScheme));
        localStorage.setItem('language', JSON.stringify(settings.value.language));
        localStorage.setItem('notificationSettings', JSON.stringify(notificationSettings.value));
        localStorage.setItem('telegramConnected', JSON.stringify(telegramConnection.value.connected));
        
        // Здесь можно добавить API вызов для сохранения настроек (мок)
        $q.notify({
            color: 'positive',
            message: 'Настройки сохранены',
            icon: 'check'
        });
    } catch (error) {
        console.error('Error saving settings:', error);
        $q.notify({
            color: 'negative',
            message: 'Ошибка при сохранении настроек',
            icon: 'error'
        });
    }
}

function startTelegramConnection() {
    // Генерируем мок-код подключения и открываем диалог
    telegramDialog.value.code = Math.floor(100000 + Math.random() * 900000).toString();
    telegramDialog.value.visible = true;
}

function confirmTelegramConnection() {
    telegramConnection.value.connected = true;
    telegramDialog.value.visible = false;
    $q.notify({ color: 'positive', icon: 'done', message: 'Telegram подключен (мок)' });
}

function disconnectTelegram() {
    telegramConnection.value.connected = false;
    notificationSettings.value.telegramEnabled = false;
    $q.notify({ color: 'warning', icon: 'link_off', message: 'Telegram отключен' });
}

function sendTestEmail() {
    if (!notificationSettings.value.emailEnabled || !notificationSettings.value.email) {
        $q.notify({ color: 'warning', icon: 'warning', message: 'Включите email-уведомления и укажите email' });
        return;
    }
    // Мок: просто показываем уведомление
    $q.notify({ color: 'positive', icon: 'outgoing_mail', message: `Тестовое письмо отправлено на ${notificationSettings.value.email}` });
}

function sendTestTelegram() {
    if (!telegramConnection.value.connected || !notificationSettings.value.telegramEnabled) {
        $q.notify({ color: 'warning', icon: 'warning', message: 'Подключите Telegram и включите уведомления' });
        return;
    }
    const username = notificationSettings.value.telegramUsername ? `@${notificationSettings.value.telegramUsername}` : 'ваш Telegram';
    // Мок: просто показываем уведомление
    $q.notify({ color: 'positive', icon: 'send', message: `Тестовое сообщение отправлено в ${username}` });
}

onMounted(() => {
    themeStore.initTheme();
    settings.value.darkMode = themeStore.isDark;

    // Загружаем сохраненную цветовую схему
    const savedColorScheme = localStorage.getItem('colorScheme');
    if (savedColorScheme) {
        try {
            const scheme = JSON.parse(savedColorScheme);
            settings.value.colorScheme = scheme;
            applyColorScheme(scheme.value);
        } catch (error) {
            console.error('Error parsing saved color scheme:', error);
            // Если ошибка парсинга, устанавливаем синюю схему по умолчанию
            settings.value.colorScheme = { label: 'Синяя', value: 'blue' };
            applyColorScheme('blue');
        }
    } else {
        // Если нет сохраненной схемы, устанавливаем синюю по умолчанию
        settings.value.colorScheme = { label: 'Синяя', value: 'blue' };
        applyColorScheme('blue');
    }

    // Загружаем сохраненный язык
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage) {
        try {
            settings.value.language = JSON.parse(savedLanguage);
        } catch (error) {
            console.error('Error parsing saved language:', error);
            settings.value.language = { label: 'Русский', value: 'ru' };
        }
    }

    // Загружаем сохраненные настройки уведомлений (мок)
    const savedNotifications = localStorage.getItem('notificationSettings');
    if (savedNotifications) {
        try {
            const parsed = JSON.parse(savedNotifications);
            notificationSettings.value = {
                email: parsed.email || '',
                emailEnabled: !!parsed.emailEnabled,
                telegramUsername: parsed.telegramUsername || '',
                telegramEnabled: !!parsed.telegramEnabled
            };
        } catch (error) {
            console.error('Error parsing notification settings:', error);
        }
    }

    const savedTelegramConnected = localStorage.getItem('telegramConnected');
    if (savedTelegramConnected) {
        try {
            telegramConnection.value.connected = JSON.parse(savedTelegramConnected) === true;
        } catch {
            telegramConnection.value.connected = false;
        }
    }
});
</script>

<style lang="scss" scoped>
.settings-page {
    background: linear-gradient(135deg, rgba(var(--app-primary-rgb, 37, 99, 235), 0.05) 0%, rgba(var(--app-secondary-rgb, 5, 150, 105), 0.05) 100%);
    min-height: 100vh;
}

.page-header {
    text-align: center;
    padding: 2rem 0;
    
    .text-h4 {
        background: linear-gradient(135deg, var(--app-gradient-start, #2563eb), var(--app-gradient-end, #059669));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
}

.settings-card {
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    height: 100%;

    &:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
    }

    .card-header {
        background: linear-gradient(135deg, rgba(var(--app-primary-rgb, 37, 99, 235), 0.1), rgba(var(--app-secondary-rgb, 5, 150, 105), 0.1));
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
    }

    .card-content {
        padding: 1.5rem;
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
}

.equal-height {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.settings-list {
    .setting-item {
        border-radius: 12px;
        margin: 8px 0;
        padding: 16px;
        transition: all 0.2s ease;
        border: 1px solid transparent;

        &:hover {
            background: rgba(var(--app-primary-rgb, 37, 99, 235), 0.05);
            border-color: rgba(var(--app-primary-rgb, 37, 99, 235), 0.1);
            transform: translateX(4px);
        }

        .q-item__section--avatar {
            min-width: 48px;
        }

        .q-item__label {
            line-height: 1.4;
        }
    }
}

.full-width-input {
    min-width: 280px;
}

.action-btn {
    border-radius: 16px;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 16px 24px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-width: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;

    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }

    &.q-btn--outline {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
}

.language-select {
    min-width: 140px;
    border-radius: 12px;
    
    .q-field__control {
        border-radius: 12px;
    }
}

.color-select {
    min-width: 140px;
    border-radius: 12px;
    
    .q-field__control {
        border-radius: 12px;
    }
}

.save-btn {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    box-shadow: 0 8px 32px rgba(37, 99, 235, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
        transform: scale(1.1);
        box-shadow: 0 12px 40px rgba(37, 99, 235, 0.4);
    }
}

.fixed-bottom-right {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 1000;
}

// Dark theme adjustments
body.body--dark {
    .settings-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .setting-item:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
    }

    .action-btn.q-btn--outline {
        background: rgba(255, 255, 255, 0.05);
    }
}

// Responsive adjustments
@media (max-width: 768px) {
    .settings-page {
        padding: 1rem;
    }
    
    .page-header {
        padding: 1rem 0;
        
        .text-h4 {
            font-size: 1.75rem;
        }
    }
    
    .settings-card {
        margin-bottom: 1rem;
    }
    
    .action-btn {
        margin-bottom: 1rem;
    }
}
</style>