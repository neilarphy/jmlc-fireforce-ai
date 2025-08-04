<template>
  <q-card class="full-height">
    <q-card-section>
      <div class="text-h6 text-weight-bold q-mb-md">Погодные условия</div>
      
      <div class="q-gutter-y-md">
        <!-- Температура -->
        <div class="flex items-center justify-between bg-grey-2 rounded-borders q-pa-sm">
          <div class="flex items-center">
            <q-icon name="thermostat" color="amber" size="sm" class="q-mr-sm" />
            <span class="text-weight-medium text-grey-8">Температура</span>
          </div>
          <span class="text-weight-bold">{{ weather.temperature }}°C</span>
        </div>
        
        <!-- Влажность -->
        <div class="flex items-center justify-between bg-grey-2 rounded-borders q-pa-sm">
          <div class="flex items-center">
            <q-icon name="water_drop" color="blue" size="sm" class="q-mr-sm" />
            <span class="text-weight-medium text-grey-8">Влажность</span>
          </div>
          <span class="text-weight-bold">{{ weather.humidity }}%</span>
        </div>
        
        <!-- Ветер -->
        <div class="flex items-center justify-between bg-grey-2 rounded-borders q-pa-sm">
          <div class="flex items-center">
            <q-icon name="air" color="grey" size="sm" class="q-mr-sm" />
            <span class="text-weight-medium text-grey-8">Ветер</span>
          </div>
          <span class="text-weight-bold">{{ weather.wind }} км/ч</span>
        </div>
        
        <!-- Осадки -->
        <div class="flex items-center justify-between bg-grey-2 rounded-borders q-pa-sm">
          <div class="flex items-center">
            <q-icon name="cloud" color="grey-6" size="sm" class="q-mr-sm" />
            <span class="text-weight-medium text-grey-8">Осадки</span>
          </div>
          <span class="text-weight-bold">{{ weather.precipitation }} мм</span>
        </div>
      </div>
      
      <!-- Предупреждение о пожарной опасности -->
      <div class="bg-amber-1 border border-amber-4 rounded-borders q-pa-md q-mt-md">
        <p class="flex items-center text-amber-9 text-weight-medium q-mb-xs">
          <q-icon name="warning" color="amber" size="xs" class="q-mr-xs" />
          <span>{{ fireRisk.level }}</span>
        </p>
        <p class="text-caption text-amber-8">Индекс пожарной опасности: {{ fireRisk.index }} из 5</p>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
defineProps({
  weather: {
    type: Object,
    default: () => ({
      temperature: 28,
      humidity: 22,
      wind: 15,
      precipitation: 0
    })
  },
  fireRisk: {
    type: Object,
    default: () => ({
      level: 'Высокая пожароопасность',
      index: 4
    })
  }
})
</script>