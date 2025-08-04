<template>
  <div class="dashboard-header-container">
    <div class="header-content">
      <h2 class="header-title">Панель управления</h2>
      <p class="header-subtitle">Мониторинг пожарной безопасности в реальном времени</p>
    </div>
    <div class="header-actions">
      <q-btn outline color="grey-7" icon="download" label="Экспорт" class="action-btn" @click="$emit('export')" no-caps
        unelevated />
      <q-btn color="red" icon="description" label="Отчет" class="action-btn" @click="$emit('report')" no-caps
        unelevated />
    </div>
  </div>
</template>

<script setup>
defineEmits(['export', 'report'])
</script>

<style lang="scss" scoped>
.dashboard-header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 72px;
  padding: 16px 0;
  gap: 24px;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    min-height: auto;
  }
}

.header-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.header-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 4px 0;
  line-height: 1.2;
}

.header-subtitle {
  font-size: 0.95rem;
  color: #6b7280;
  margin: 0;
  line-height: 1.4;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;

  @media (max-width: 768px) {
    width: 100%;
    justify-content: flex-start;
  }
}

.action-btn {
  border-radius: 8px;
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}

body.body--dark {
  .header-title {
    color: #f8fafc;
  }

  .header-subtitle {
    color: #cbd5e1;
  }
}
</style>