<template>
  <q-card class="modern-card">
    <q-card-section>
      <div class="text-h6 text-weight-bold">Создать прогноз пожарной опасности</div>
      <p class="text-grey-8 q-mt-xs">Получите прогноз для указанных координат или найдите место по названию</p>
    </q-card-section>

    <q-card-section>
      <q-form @submit="createPrediction" class="q-gutter-md">
        <!-- Поиск по названию места -->
        <q-input
          filled
          v-model="locationSearch"
          label="Поиск места"
          placeholder="Введите название города или региона"
          clearable
          @update:model-value="onLocationSearch"
          :loading="searchLoading"
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
          <template v-slot:append v-if="locationSearch">
            <q-btn
              flat
              round
              dense
              icon="my_location"
              @click="getCurrentLocation"
              :loading="locationLoading"
            >
              <q-tooltip>Использовать текущее местоположение</q-tooltip>
            </q-btn>
          </template>
        </q-input>

        <!-- Автокомплит результаты -->
        <q-list v-if="locationSuggestions.length > 0" bordered separator class="rounded-borders">
          <q-item
            v-for="suggestion in locationSuggestions"
            :key="suggestion.id"
            clickable
            @click="selectLocation(suggestion)"
            class="suggestion-item"
          >
            <q-item-section avatar>
              <q-icon name="place" color="primary" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ suggestion.name }}</q-item-label>
              <q-item-label caption>{{ suggestion.region }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-item-label caption>{{ suggestion.coordinates }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>

        <!-- Координаты -->
        <div class="row q-col-gutter-md">
          <div class="col-6">
            <q-input
              filled
              v-model.number="form.latitude"
              label="Широта"
              type="number"
              step="0.000001"
              :rules="[val => val >= -90 && val <= 90 || 'Введите корректную широту (-90 до 90)']"
            />
          </div>
          <div class="col-6">
            <q-input
              filled
              v-model.number="form.longitude"
              label="Долгота"
              type="number"
              step="0.000001"
              :rules="[val => val >= -180 && val <= 180 || 'Введите корректную долготу (-180 до 180)']"
            />
          </div>
        </div>

        <!-- Кнопка создания прогноза -->
        <q-btn
          label="Создать прогноз"
          type="submit"
          color="primary"
          class="full-width q-py-md"
          :loading="predictionLoading"
          :disable="!isFormValid"
          no-caps
        >
          <template v-slot:loading>
            <q-spinner-hourglass class="on-left" />
            Создание прогноза...
          </template>
        </q-btn>
      </q-form>
    </q-card-section>

    <!-- Статус выполнения задачи -->
    <q-card-section v-if="currentTask">
      <q-separator class="q-mb-md" />
      <div class="text-subtitle2 q-mb-sm">Статус выполнения</div>
      
      <div class="row items-center q-mb-md">
        <div class="col">
          <q-linear-progress
            :value="currentTask.progress / 100"
            color="primary"
            size="20px"
            class="rounded-borders"
          >
            <div class="absolute-full flex flex-center">
              <q-badge color="white" text-color="primary" :label="`${currentTask.progress}%`" />
            </div>
          </q-linear-progress>
        </div>
        <div class="col-auto q-ml-md">
          <q-btn
            flat
            round
            dense
            icon="refresh"
            @click="refreshTaskStatus"
            :loading="statusLoading"
          >
            <q-tooltip>Обновить статус</q-tooltip>
          </q-btn>
        </div>
      </div>

      <div class="text-body2 text-grey-8">
        <q-icon name="info" class="q-mr-xs" />
        {{ currentTask.status }}
      </div>

      <div v-if="currentTask.stage" class="text-caption text-grey-6 q-mt-xs">
        Этап: {{ getStageLabel(currentTask.stage) }}
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import ApiService from 'src/services/api'

const $q = useQuasar()

const props = defineProps({
  initialCoordinates: {
    type: Object,
    default: () => ({ latitude: 55.7558, longitude: 37.6173 })
  }
})

const emit = defineEmits(['prediction-created', 'prediction-updated'])

const form = ref({
  latitude: props.initialCoordinates.latitude,
  longitude: props.initialCoordinates.longitude
})

const locationSearch = ref('')
const locationSuggestions = ref([])
const currentTask = ref(null)

const predictionLoading = ref(false)
const searchLoading = ref(false)
const locationLoading = ref(false)
const statusLoading = ref(false)

let searchTimeout = null
let statusPollingInterval = null

const isFormValid = computed(() => {
  return form.value.latitude >= -90 && form.value.latitude <= 90 &&
         form.value.longitude >= -180 && form.value.longitude <= 180
})

async function createPrediction() {
  if (!isFormValid.value) return

  predictionLoading.value = true
  
  try {
    const response = await ApiService.createPrediction({
      latitude: form.value.latitude,
      longitude: form.value.longitude
    })

    if (response.success && response.task_id) {
      currentTask.value = {
        id: response.task_id,
        progress: 0,
        status: 'Задача добавлена в очередь',
        stage: 'pending'
      }

      startStatusPolling(response.task_id)

      $q.notify({
        color: 'positive',
        message: 'Прогноз создается...',
        icon: 'schedule',
        timeout: 2000
      })
    }
  } catch (error) {
    console.error('Error creating prediction:', error)
    $q.notify({
      color: 'negative',
      message: 'Ошибка создания прогноза',
      icon: 'error'
    })
  } finally {
    predictionLoading.value = false
  }
}

async function onLocationSearch(value) {
  if (!value || value.length < 3) {
    locationSuggestions.value = []
    return
  }

  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  searchTimeout = setTimeout(async () => {
    searchLoading.value = true
    try {
      const suggestions = await ApiService.getLocationSuggestions(value)
      locationSuggestions.value = suggestions.locations || []
    } catch (error) {
      console.error('Error searching locations:', error)
      locationSuggestions.value = []
    } finally {
      searchLoading.value = false
    }
  }, 500)
}

function selectLocation(suggestion) {
  form.value.latitude = suggestion.latitude
  form.value.longitude = suggestion.longitude
  locationSearch.value = suggestion.name
  locationSuggestions.value = []
}

async function getCurrentLocation() {
  if (!navigator.geolocation) {
    $q.notify({
      color: 'negative',
      message: 'Геолокация не поддерживается вашим браузером',
      icon: 'error'
    })
    return
  }

  locationLoading.value = true

  navigator.geolocation.getCurrentPosition(
    (position) => {
      form.value.latitude = position.coords.latitude
      form.value.longitude = position.coords.longitude
      locationSearch.value = 'Текущее местоположение'
      
      $q.notify({
        color: 'positive',
        message: 'Местоположение определено',
        icon: 'my_location'
      })
      
      locationLoading.value = false
    },
    (error) => {
      console.error('Geolocation error:', error)
      $q.notify({
        color: 'negative',
        message: 'Не удалось определить местоположение',
        icon: 'error'
      })
      locationLoading.value = false
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 300000
    }
  )
}

function startStatusPolling(taskId) {
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval)
  }

  statusPollingInterval = setInterval(async () => {
    await checkTaskStatus(taskId)
  }, 2000)
}

async function checkTaskStatus(taskId) {
  try {
    const status = await ApiService.getPredictionStatus(taskId)
    
    currentTask.value = {
      id: taskId,
      progress: status.progress || 0,
      status: status.status || 'Обработка...',
      stage: status.stage || 'processing',
      state: status.state
    }

    if (status.state === 'SUCCESS') {
      clearInterval(statusPollingInterval)
      statusPollingInterval = null
      
      emit('prediction-created', status.result)
      
      $q.notify({
        color: 'positive',
        message: 'Прогноз готов!',
        icon: 'check_circle',
        timeout: 3000
      })

      setTimeout(() => {
        currentTask.value = null
      }, 5000)
    } else if (status.state === 'FAILURE') {
      clearInterval(statusPollingInterval)
      statusPollingInterval = null
      
      $q.notify({
        color: 'negative',
        message: 'Ошибка при создании прогноза',
        icon: 'error'
      })

      currentTask.value = null
    }
  } catch (error) {
    console.error('Error checking task status:', error)
  }
}

async function refreshTaskStatus() {
  if (!currentTask.value?.id) return
  
  statusLoading.value = true
  await checkTaskStatus(currentTask.value.id)
  statusLoading.value = false
}

function getStageLabel(stage) {
  const stages = {
    'pending': 'Ожидание',
    'processing': 'Обработка',
    'prediction': 'Создание прогноза',
    'completed': 'Завершено',
    'failed': 'Ошибка'
  }
  return stages[stage] || stage
}

function cleanup() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval)
  }
}

watch(() => [form.value.latitude, form.value.longitude], () => {
  emit('prediction-updated', { ...form.value })
})

import { onUnmounted } from 'vue'
onUnmounted(() => {
  cleanup()
})
</script>

<style lang="scss" scoped>
.modern-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
  }
}

.suggestion-item {
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: rgba(25, 118, 210, 0.04);
  }
}

:deep(.q-field--filled .q-field__control) {
  border-radius: 8px;
}

:deep(.q-btn) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}

:deep(.q-linear-progress) {
  border-radius: 10px;
}
</style>