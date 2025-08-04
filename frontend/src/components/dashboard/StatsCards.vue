<template>
  <div class="row q-col-gutter-md">
    <!-- Карточка 1: Активные пожары -->
    <div class="col-12 col-md-6 col-lg-3">
      <q-card class="fire-card">
        <q-card-section class="relative-position">
          <div class="absolute-full fire-bg">
            <q-icon name="local_fire_department" size="150px" class="text-white opacity-10" />
          </div>
          <div class="relative-position flex items-center justify-between q-mb-md">
            <div class="bg-white bg-opacity-20 rounded-borders p-3 shadow-1">
              <q-icon name="local_fire_department" size="24px" class="text-white" />
            </div>
            <span class="text-h3 text-weight-bold">{{ stats.activeFires }}</span>
          </div>
          <p class="text-h6 text-weight-medium q-mb-xs">Активные пожары</p>
          <p class="text-subtitle2 opacity-8">↑ {{ stats.firesTrend }} за последний час</p>
        </q-card-section>
      </q-card>
    </div>

    <!-- Карточка 2: Зоны высокого риска -->
    <div class="col-12 col-md-6 col-lg-3">
      <q-card class="warning-card">
        <q-card-section class="relative-position">
          <div class="absolute-full warning-bg">
            <q-icon name="warning" size="150px" class="text-white opacity-10" />
          </div>
          <div class="relative-position flex items-center justify-between q-mb-md">
            <div class="bg-white bg-opacity-20 rounded-borders p-3 shadow-1">
              <q-icon name="warning" size="24px" class="text-white" />
            </div>
            <span class="text-h3 text-weight-bold">{{ stats.highRiskZones }}</span>
          </div>
          <p class="text-h6 text-weight-medium q-mb-xs">Зоны высокого риска</p>
          <p class="text-subtitle2 opacity-8">↓ {{ stats.riskTrend }} с вчерашнего дня</p>
        </q-card-section>
      </q-card>
    </div>

    <!-- Карточка 3: Точность прогноза -->
    <div class="col-12 col-md-6 col-lg-3">
      <q-card class="accuracy-card">
        <q-card-section class="relative-position">
          <div class="absolute-full accuracy-bg">
            <q-icon name="trending_up" size="150px" class="text-white opacity-10" />
          </div>
          <div class="relative-position flex items-center justify-between q-mb-md">
            <div class="bg-white bg-opacity-20 rounded-borders p-3 shadow-1">
              <q-icon name="show_chart" size="24px" class="text-white" />
            </div>
            <span class="text-h3 text-weight-bold">{{ stats.accuracy }}%</span>
          </div>
          <p class="text-h6 text-weight-medium q-mb-xs">Точность прогноза</p>
          <p class="text-subtitle2 opacity-8">За последние 30 дней</p>
        </q-card-section>
      </q-card>
    </div>

    <!-- Карточка 4: Активные команды -->
    <div class="col-12 col-md-6 col-lg-3">
      <q-card class="teams-card">
        <q-card-section class="relative-position">
          <div class="absolute-full teams-bg">
            <q-icon name="security" size="150px" class="text-white opacity-10" />
          </div>
          <div class="relative-position flex items-center justify-between q-mb-md">
            <div class="bg-white bg-opacity-20 rounded-borders p-3 shadow-1">
              <q-icon name="security" size="24px" class="text-white" />
            </div>
            <span class="text-h3 text-weight-bold">{{ stats.activeTeams }}</span>
          </div>
          <p class="text-h6 text-weight-medium q-mb-xs">Активные команды</p>
          <p class="text-subtitle2 opacity-8">{{ stats.teamReadiness }}% готовности</p>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Object,
    default: () => ({
      activeFires: 12,
      firesTrend: 3,
      highRiskZones: 28,
      riskTrend: 2,
      accuracy: 85,
      activeTeams: 156,
      teamReadiness: 98
    })
  }
})
</script>

<style lang="scss" scoped>
.fire-card {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(239, 68, 68, 0.3), 0 10px 10px -5px rgba(239, 68, 68, 0.1);
  }
}

.warning-card {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(245, 158, 11, 0.3), 0 10px 10px -5px rgba(245, 158, 11, 0.1);
  }
}

.accuracy-card {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(59, 130, 246, 0.3), 0 10px 10px -5px rgba(59, 130, 246, 0.1);
  }
}

.teams-card {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(16, 185, 129, 0.3), 0 10px 10px -5px rgba(16, 185, 129, 0.1);
  }
}

.opacity-8 {
  opacity: 0.8;
}

.opacity-10 {
  opacity: 0.1;
}

.bg-opacity-20 {
  background-color: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}
</style>