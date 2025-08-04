<template>
  <q-layout view="lHh Lpr lFf" :class="$q.dark.isActive ? 'bg-grey-10' : 'bg-grey-1'">
    <!-- Боковая панель -->
    <q-drawer 
      v-model="leftDrawerOpen" 
      show-if-above 
      :width="isCollapsed ? 70 : 260"
      :class="$q.dark.isActive ? 'bg-grey-9 text-white' : 'bg-dark text-white'" 
      :breakpoint="0"
      :mini="isCollapsed"
    >
      <div class="column full-height">
        <!-- Заголовок боковой панели -->
        <div class="q-pa-md border-bottom" :class="isCollapsed ? 'text-center' : ''">
          <div v-if="!isCollapsed" class="row items-center cursor-pointer" @click="toggleDrawer">
            <q-icon name="local_fire_department" color="red" size="28px" class="q-mr-sm" />
            <div class="text-h6 text-weight-bold">FireForceAI</div>
          </div>
          <div v-else class="flex justify-center">
            <q-icon 
              name="local_fire_department" 
              color="red" 
              size="32px" 
              class="cursor-pointer"
              @click="toggleDrawer"
            />
          </div>
        </div>

        <!-- Навигационное меню -->
        <q-scroll-area class="col">
          <q-list :padding="!isCollapsed">
            <q-item 
              v-for="item in allMenuItems" 
              :key="item.id" 
              clickable 
              v-ripple 
              :to="item.route"
              :active="$route.path === item.route"
              :class="[
                $route.path === item.route ? 'bg-primary text-white' : 'text-grey-4',
                isCollapsed ? 'mini-item q-my-xs' : 'q-my-sm rounded-borders'
              ]"
            >
              <q-item-section avatar :class="isCollapsed ? 'mini-avatar' : ''">
                <div class="relative-position icon-container">
                  <q-icon :name="item.icon" :size="isCollapsed ? '24px' : '20px'" />
                  <q-badge 
                    v-if="item.notifications && isCollapsed" 
                    color="red" 
                    floating 
                    rounded
                    style="top: -8px; right: -8px;"
                  >
                    {{ item.notifications }}
                  </q-badge>
                </div>
              </q-item-section>
              
              <q-item-section v-if="!isCollapsed">
                <q-item-label>{{ item.label }}</q-item-label>
              </q-item-section>
              
              <q-item-section v-if="item.notifications && !isCollapsed" side>
                <q-badge color="red" rounded>{{ item.notifications }}</q-badge>
              </q-item-section>
              
              <q-tooltip v-if="isCollapsed" anchor="center right" self="center left" :offset="[10, 0]">
                {{ item.label }}
              </q-tooltip>
            </q-item>
          </q-list>
        </q-scroll-area>

        <!-- Нижняя панель с кнопками -->
        <div class="q-pa-md border-top">
          <!-- Информация о пользователе -->
          <div class="q-mb-md" :class="isCollapsed ? 'text-center' : ''">
            <!-- В свернутом состоянии - только аватар -->
            <div v-if="isCollapsed" class="column items-center">
              <q-avatar size="36px" color="primary" text-color="white" class="q-mb-xs">
                <q-icon name="person" />
              </q-avatar>
              <q-tooltip anchor="center right" self="center left" :offset="[10, 0]">
                {{ authStore.user?.full_name || authStore.user?.username || 'Пользователь' }}<br>
                {{ authStore.user?.email || '' }}
              </q-tooltip>
            </div>
            
            <!-- В развернутом состоянии - аватар с информацией -->
            <div v-else class="row items-center">
              <q-avatar size="36px" color="primary" text-color="white" class="q-mr-sm">
                <q-icon name="person" />
              </q-avatar>
              <div class="col">
                <div class="text-body2 text-weight-medium text-grey-3">
                  {{ authStore.user?.full_name || authStore.user?.username || 'Пользователь' }}
                </div>
                <div class="text-caption text-grey-5">
                  {{ authStore.user?.email || '' }}
                </div>
              </div>
            </div>
          </div>

          <!-- Кнопки управления -->
          <div class="column" :class="isCollapsed ? 'items-center' : ''">
            <!-- В свернутом состоянии - кнопки вертикально -->
            <template v-if="isCollapsed">
              <q-btn 
                @click="toggleDrawer"
                icon="keyboard_arrow_right"
                flat
                round
                color="grey-4"
                size="sm"
                class="q-mb-xs"
              >
                <q-tooltip anchor="center right" self="center left" :offset="[10, 0]">
                  Развернуть меню
                </q-tooltip>
              </q-btn>

              <q-btn 
                @click="handleLogout"
                icon="logout"
                flat
                round
                color="red-4"
                size="sm"
              >
                <q-tooltip anchor="center right" self="center left" :offset="[10, 0]">
                  Выйти из системы
                </q-tooltip>
              </q-btn>
            </template>

            <!-- В развернутом состоянии - кнопки горизонтально -->
            <template v-else>
              <div class="row justify-between">
                <q-btn 
                  @click="toggleDrawer"
                  icon="keyboard_arrow_left"
                  flat
                  round
                  color="grey-4"
                  size="sm"
                >
                  <q-tooltip>
                    Свернуть меню
                  </q-tooltip>
                </q-btn>

                <q-btn 
                  @click="handleLogout"
                  icon="logout"
                  flat
                  round
                  color="red-4"
                  size="sm"
                >
                  <q-tooltip>
                    Выйти из системы
                  </q-tooltip>
                </q-btn>
              </div>
            </template>
          </div>

          <!-- Копирайт (только в развернутом режиме) -->
          <div v-if="!isCollapsed" class="text-grey-6 text-caption text-center q-mt-md">
            &copy; 2025 FireForceAI
          </div>
        </div>
      </div>
    </q-drawer>

    <!-- Основной контент -->
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, provide, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'
import { useQuasar } from 'quasar'

const $route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const $q = useQuasar()

const allMenuItems = computed(() => [
  { id: 'dashboard', label: 'Панель управления', icon: 'home', route: '/' },
  { id: 'map', label: 'Карта рисков', icon: 'map', route: '/map' },
  { id: 'predictions', label: 'Прогнозы', icon: 'trending_up', route: '/predictions' },
  { id: 'history', label: 'История пожаров', icon: 'history', route: '/history' },
  { 
    id: 'alerts', 
    label: 'Оповещения', 
    icon: 'notifications', 
    route: '/alerts',
    notifications: notifications.value.alerts > 0 ? notifications.value.alerts : null
  },
  { id: 'analytics', label: 'Аналитика', icon: 'bar_chart', route: '/analytics' },
  { id: 'team', label: 'Команда', icon: 'people', route: '/team' },
  { id: 'settings', label: 'Настройки', icon: 'settings', route: '/settings' }
])

const leftDrawerOpen = ref(true)
const isCollapsed = ref(true)

const notifications = ref({
  alerts: 0
})

function toggleDrawer() {
  isCollapsed.value = !isCollapsed.value
}

provide('toggleDrawer', toggleDrawer)

function handleLogout() {
  $q.dialog({
    title: 'Выход из системы',
    message: 'Вы уверены, что хотите выйти?',
    cancel: {
      label: 'Отмена',
      color: 'grey',
      flat: true
    },
    ok: {
      label: 'Выйти',
      color: 'negative',
      unelevated: true
    },
    persistent: true
  }).onOk(() => {
    authStore.logout()
    $q.notify({
      color: 'positive',
      message: 'Вы успешно вышли из системы',
      icon: 'logout',
      position: 'top'
    })
    router.push('/login')
  })
}
</script>

<style lang="scss">
.border-bottom {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.border-top {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.bg-dark {
  background-color: #1e1e2d;
}

.q-drawer {
  .q-list .q-item {
    transition: all 0.2s ease;
    
    &:hover {
      background-color: rgba(255, 255, 255, 0.1);
    }
  }
}

.q-drawer--mini {
  .mini-item {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    padding: 8px 0 !important;
    width: 100% !important;
    
    .mini-avatar {
      min-width: auto !important;
      padding: 0 !important;
      margin: 0 !important;
      justify-content: center !important;
      align-items: center !important;
      flex: none !important;
      
      .icon-container {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
      }
    }
    
    .q-item__section:not(.mini-avatar) {
      display: none !important;
    }
  }
}
</style>