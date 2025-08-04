<template>
  <q-card v-if="prediction" class="modern-card">
    <q-card-section>
      <div class="text-h6 text-weight-bold">Результат прогноза</div>
      <p class="text-grey-8 q-mt-xs">
        {{ prediction.location || `${prediction.latitude?.toFixed(4)}, ${prediction.longitude?.toFixed(4)}` }}
      </p>
    </q-card-section>

    <q-card-section>
      <!-- Основной индикатор риска -->
      <div class="text-center q-mb-lg">
        <q-circular-progress
          show-value
          font-size="18px"
          :value="prediction.fire_probability * 100"
          size="140px"
          :color="getRiskColor(prediction.risk_level)"
          track-color="grey-3"
          class="q-ma-md"
          :thickness="0.15"
        >
          {{ Math.round(prediction.fire_probability * 100) }}%
        </q-circular-progress>
        
        <div class="q-mt-md">
          <q-badge
            :color="getRiskColor(prediction.risk_level)"
            class="text-h6 q-px-md q-py-sm"
            style="border-radius: 20px;"
          >
            {{ getRiskLabel(prediction.risk_level) }}
          </q-badge>
        </div>
      </div>

      <!-- Уверенность модели -->
      <div class="q-mb-md">
        <div class="row items-center q-mb-xs">
          <div class="text-subtitle2">Уверенность модели</div>
          <q-space />
          <div class="text-weight-bold">{{ Math.round(prediction.confidence * 100) }}%</div>
        </div>
        <q-linear-progress
          size="20px"
          :value="prediction.confidence"
          color="blue"
          class="rounded-borders"
        >
          <div class="absolute-full flex flex-center">
            <q-badge
              color="white"
              text-color="primary"
              :label="`${Math.round(prediction.confidence * 100)}%`"
            />
          </div>
        </q-linear-progress>
      </div>

      <!-- Погодные условия -->
      <div class="q-mb-md">
        <div class="text-subtitle2 q-mb-sm">Погодные условия</div>
        <div class="row q-col-gutter-sm">
          <div class="col-6">
            <q-card flat bordered class="weather-card">
              <q-card-section class="text-center q-pa-sm">
                <q-icon name="thermostat" color="red" size="24px" />
                <div class="text-caption text-grey-8">Температура</div>
                <div class="text-h6">{{ prediction.temperature }}°C</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6">
            <q-card flat bordered class="weather-card">
              <q-card-section class="text-center q-pa-sm">
                <q-icon name="water_drop" color="blue" size="24px" />
                <div class="text-caption text-grey-8">Влажность</div>
                <div class="text-h6">{{ prediction.humidity }}%</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6">
            <q-card flat bordered class="weather-card">
              <q-card-section class="text-center q-pa-sm">
                <q-icon name="air" color="cyan" size="24px" />
                <div class="text-caption text-grey-8">Ветер</div>
                <div class="text-h6">{{ prediction.wind_speed }} м/с</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6">
            <q-card flat bordered class="weather-card">
              <q-card-section class="text-center q-pa-sm">
                <q-icon name="grain" color="purple" size="24px" />
                <div class="text-caption text-grey-8">Осадки</div>
                <div class="text-h6">{{ prediction.precipitation || 0 }} мм</div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>

      <!-- Факторы риска -->
      <div v-if="prediction.risk_factors && prediction.risk_factors.length > 0" class="q-mb-md">
        <div class="text-subtitle2 q-mb-sm">Факторы риска</div>
        <q-list dense>
          <q-item
            v-for="(factor, index) in prediction.risk_factors"
            :key="index"
            class="risk-factor-item"
          >
            <q-item-section avatar>
              <q-icon
                :name="getRiskFactorIcon(factor.type)"
                :color="getRiskFactorColor(factor.impact)"
                size="20px"
              />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ factor.name }}</q-item-label>
              <q-item-label caption>{{ factor.description }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-badge
                :color="getRiskFactorColor(factor.impact)"
                :label="getImpactLabel(factor.impact)"
              />
            </q-item-section>
          </q-item>
        </q-list>
      </div>

      <!-- Рекомендации -->
      <div v-if="prediction.recommendations && prediction.recommendations.length > 0" class="q-mb-md">
        <div class="text-subtitle2 q-mb-sm">Рекомендации</div>
        <q-list dense>
          <q-item
            v-for="(recommendation, index) in prediction.recommendations"
            :key="index"
            class="recommendation-item"
          >
            <q-item-section avatar>
              <q-icon name="lightbulb" color="orange" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ recommendation.title }}</q-item-label>
              <q-item-label caption>{{ recommendation.description }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-badge
                :color="getRecommendationColor(recommendation.priority)"
                :label="recommendation.priority"
              />
            </q-item-section>
          </q-item>
        </q-list>
      </div>

      <!-- Метаинформация -->
      <div class="q-mt-md q-pt-md" style="border-top: 1px solid #e0e0e0;">
        <div class="row q-col-gutter-md text-caption text-grey-6">
          <div class="col-6">
            <div>Модель: {{ prediction.model_version || 'v1.0' }}</div>
          </div>
          <div class="col-6">
            <div>Создано: {{ formatDate(prediction.created_at) }}</div>
          </div>
        </div>
      </div>
    </q-card-section>

    <!-- Действия -->
    <q-card-actions align="right">
      <q-btn
        flat
        color="primary"
        label="Показать на карте"
        icon="map"
        @click="showOnMap"
        no-caps
      />
      <q-btn
        flat
        color="secondary"
        label="Поделиться"
        icon="share"
        @click="sharePrediction"
        no-caps
      />
      <q-btn
        flat
        color="info"
        label="Подробнее"
        icon="info"
        @click="showDetails"
        no-caps
      />
    </q-card-actions>
  </q-card>
</template>

<script setup>
import { useQuasar } from 'quasar'

const $q = useQuasar()

const props = defineProps({
  prediction: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['show-on-map', 'show-details'])

function getRiskColor(riskLevel) {
  const colors = {
    'low': 'green',
    'medium': 'yellow-8',
    'high': 'orange',
    'critical': 'red'
  }
  return colors[riskLevel] || 'grey'
}

function getRiskLabel(riskLevel) {
  const labels = {
    'low': 'Низкий риск',
    'medium': 'Средний риск',
    'high': 'Высокий риск',
    'critical': 'Критический риск'
  }
  return labels[riskLevel] || 'Неизвестно'
}

function getRiskFactorIcon(type) {
  const icons = {
    'temperature': 'thermostat',
    'humidity': 'water_drop',
    'wind': 'air',
    'vegetation': 'park',
    'terrain': 'terrain',
    'season': 'calendar_today'
  }
  return icons[type] || 'warning'
}

function getRiskFactorColor(impact) {
  const colors = {
    'high': 'red',
    'medium': 'orange',
    'low': 'green'
  }
  return colors[impact] || 'grey'
}

function getImpactLabel(impact) {
  const labels = {
    'high': 'Высокий',
    'medium': 'Средний',
    'low': 'Низкий'
  }
  return labels[impact] || impact
}

function getRecommendationColor(priority) {
  const colors = {
    'urgent': 'red',
    'high': 'orange',
    'medium': 'blue',
    'low': 'green'
  }
  return colors[priority] || 'grey'
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function showOnMap() {
  emit('show-on-map', props.prediction)
}

function showDetails() {
  emit('show-details', props.prediction)
}

function sharePrediction() {
  const shareData = {
    title: 'Прогноз пожарной опасности',
    text: `Риск пожара: ${Math.round(props.prediction.fire_probability * 100)}% (${getRiskLabel(props.prediction.risk_level)})`,
    url: window.location.href
  }

  if (navigator.share) {
    navigator.share(shareData)
  } else {
    const textToCopy = `${shareData.title}\n${shareData.text}\n${shareData.url}`
    navigator.clipboard.writeText(textToCopy).then(() => {
      $q.notify({
        color: 'positive',
        message: 'Ссылка скопирована в буфер обмена',
        icon: 'content_copy'
      })
    })
  }
}
</script>

<style lang="scss" scoped>
.modern-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.weather-card {
  border-radius: 8px;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
  }
}

.risk-factor-item,
.recommendation-item {
  border-radius: 8px;
  margin: 2px 0;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.02);
  }
}

:deep(.q-circular-progress) {
  font-weight: bold;
}

:deep(.q-linear-progress) {
  border-radius: 10px;
}

:deep(.q-badge) {
  font-weight: 500;
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
</style>