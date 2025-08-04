<template>
  <q-card class="full-height modern-card">
    <q-card-section class="flex justify-between items-center event-header">
      <div class="text-h6 text-weight-bold">Последние события</div>
      <q-btn flat color="red" label="Все события" icon-right="chevron_right" dense no-caps class="hover-btn" />
    </q-card-section>

    <q-card-section class="q-pa-none">
      <q-list separator>
        <q-item v-for="(event, index) in events" :key="index" class="q-pa-md">
          <q-item-section avatar>
            <q-avatar :color="event.color" text-color="white">
              <q-icon :name="event.icon" />
            </q-avatar>
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-weight-medium">{{ event.title }}</q-item-label>
            <q-item-label caption>{{ event.description }}</q-item-label>
            <div v-if="event.location" class="flex items-center text-grey-7 text-caption q-mt-xs">
              <q-icon name="place" size="xs" class="q-mr-xs" />
              <span>{{ event.location }}</span>
            </div>
            <div v-if="event.details" class="text-caption text-grey-7 q-mt-xs">
              {{ event.details }}
            </div>
          </q-item-section>
          <q-item-section side>
            <div class="text-caption text-grey">{{ event.time }}</div>
            <q-btn v-if="event.action" flat :color="event.color" :label="event.action" dense class="q-mt-xs" />
          </q-item-section>
        </q-item>
      </q-list>
    </q-card-section>
  </q-card>
</template>

<script setup>
defineProps({
  events: {
    type: Array,
    default: () => [
      {
        title: 'Новый пожар обнаружен',
        description: 'Сектор А-12, площадь возгорания ~2 га',
        location: '55.7558° N, 37.6173° E',
        time: '5 мин назад',
        icon: 'local_fire_department',
        color: 'red',
        action: 'Подробнее'
      },
      {
        title: 'Повышенный риск',
        description: 'Зона B-7 переведена в статус высокого риска',
        details: 'Температура: 32°C, Влажность: 15%',
        time: '15 мин назад',
        icon: 'warning',
        color: 'amber'
      },
      {
        title: 'Пожар локализован',
        description: 'Сектор C-3, площадь 8 га, ущерб минимальный',
        time: '1 час назад',
        icon: 'check_circle',
        color: 'teal'
      }
    ]
  }
})
</script>