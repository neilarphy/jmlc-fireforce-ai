<template>
  <q-page class="map-page q-pa-lg">
    <!-- Заголовок страницы -->
    <div class="page-header q-mb-xl">
      <div class="text-h4 text-weight-bold text-primary">Карта рисков</div>
      <div class="text-subtitle1 text-grey-6 q-mt-sm">Интерактивная карта пожарной опасности в России</div>
    </div>

    <div class="row q-col-gutter-xl">
      <!-- Map Controls -->
      <div class="col-12">
        <q-card class="dashboard-card controls-card">
          <q-card-section class="card-header">
            <div class="row items-center">
              <q-icon name="tune" size="28px" color="primary" class="q-mr-md" />
              <div>
                <div class="text-h6 text-weight-bold">Фильтры и поиск</div>
                <div class="text-caption text-grey-6">Настройте отображение данных на карте</div>
              </div>
            </div>
          </q-card-section>
          <q-card-section class="card-content">
            <div class="row items-center q-col-gutter-lg">
              <div class="col-12 col-md-3">
                <q-input outlined dense v-model="searchQuery" label="Поиск по региону" clearable class="search-input"
                  @update:model-value="applyFilters">
                  <template v-slot:append>
                    <q-icon name="search" />
                  </template>
                </q-input>
              </div>
              <div class="col-12 col-md-3">
                <q-select outlined dense v-model="selectedRegion" :options="regionOptions" label="Регион"
                  @update:model-value="applyFilters" />
              </div>
              <div class="col-12 col-md-3">
                <q-select outlined dense v-model="riskLevel" :options="riskLevels" label="Уровень риска"
                  @update:model-value="applyFilters" />
              </div>
              <div class="col-12 col-md-3">
                <q-select outlined dense v-model="timeRange" :options="timeRanges" label="Период"
                  @update:model-value="applyFilters" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Main Map -->
      <div class="col-12 col-lg-8">
        <!-- Legend над картой -->
        <q-card class="dashboard-card q-mb-md legend-over-map">
          <q-card-section class="card-content">
            <div class="row q-col-gutter-md">
              <div class="col-6 col-sm-3" v-for="(item, index) in legendItems" :key="index">
                <div class="flex items-center legend-item">
                  <div class="legend-indicator" :class="item.class"></div>
                  <span class="q-ml-sm text-caption">{{ item.label }}</span>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <q-card class="dashboard-card map-card full-height">
          <q-card-section class="card-header">
            <div class="row items-center justify-between">
              <div class="row items-center">
                <q-icon name="map" size="28px" color="primary" class="q-mr-md" />
                <div>
                  <div class="text-h6 text-weight-bold">Карта пожарной опасности</div>
                  <div class="text-caption text-grey-6">Интерактивная карта рисков возникновения пожаров в России</div>
                </div>
              </div>
              <div>
                <q-btn-group flat class="map-controls">
                  <q-btn flat round icon="my_location" @click="centerMapOnCurrentLocation" class="control-btn">
                    <q-tooltip>Моё местоположение</q-tooltip>
                  </q-btn>
                  <q-btn flat round icon="zoom_in" @click="zoomIn" class="control-btn">
                    <q-tooltip>Приблизить</q-tooltip>
                  </q-btn>
                  <q-btn flat round icon="zoom_out" @click="zoomOut" class="control-btn">
                    <q-tooltip>Отдалить</q-tooltip>
                  </q-btn>
                  <q-btn flat round icon="refresh" @click="refreshMap" class="control-btn">
                    <q-tooltip>Обновить данные</q-tooltip>
                  </q-btn>
                </q-btn-group>
              </div>
            </div>
          </q-card-section>
          <q-card-section class="card-content q-pa-none">
            <div class="map-container">
              <div id="risk-map" style="height: 100%; border-radius: 8px; overflow: hidden;"></div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Sidebar -->
      <div class="col-12 col-lg-4">
        <!-- Risk Regions -->
        <q-card class="dashboard-card q-mb-lg">
          <q-card-section class="card-header">
            <div class="row items-center">
              <q-icon name="warning" size="28px" color="orange" class="q-mr-md" />
              <div>
                <div class="text-h6 text-weight-bold">Регионы высокого риска</div>
                <div class="text-caption text-grey-6">Наиболее опасные территории</div>
              </div>
            </div>
          </q-card-section>
          <q-card-section class="card-content">
            <div class="text-center q-pa-md">
              <q-icon name="info" size="48px" color="grey-6" />
              <div class="text-grey-6 q-mt-sm">Зоны рассчитываются динамически на основе данных о пожарах</div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Statistics -->
        <q-card class="dashboard-card">
          <q-card-section class="card-header">
            <div class="row items-center">
              <q-icon name="analytics" size="28px" color="green" class="q-mr-md" />
              <div>
                <div class="text-h6 text-weight-bold">Статистика</div>
                <div class="text-caption text-grey-6">Актуальные данные</div>
              </div>
            </div>
          </q-card-section>
          <q-card-section class="card-content">
            <div class="row q-col-gutter-md">
              <div class="col-6">
                <div class="text-center stat-item">
                  <div class="text-h4 text-primary text-weight-bold">{{ fireStats.total }}</div>
                  <div class="text-caption text-grey-6">Всего пожаров</div>
                </div>
              </div>
              <div class="col-6">
                <div class="text-center stat-item">
                  <div class="text-h4 text-orange text-weight-bold">{{ fireStats.active }}</div>
                  <div class="text-caption text-grey-6">Активных</div>
                </div>
              </div>
              <div class="col-6">
                <div class="text-center stat-item">
                  <div class="text-h4 text-negative text-weight-bold">{{ fireStats.critical }}</div>
                  <div class="text-caption text-grey-6">Критических</div>
                </div>
              </div>
              <div class="col-6">
                <div class="text-center stat-item">
                  <div class="text-h4 text-positive text-weight-bold">{{ fireStats.extinguished }}</div>
                  <div class="text-caption text-grey-6">Потушено</div>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Модальное окно для информации о пожаре -->
    <q-dialog v-model="fireDetailsDialog" @keydown.esc="fireDetailsDialog = false">
      <q-card class="fire-info-modal" style="background-color: #1e293b; color: white; min-width: 400px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">{{ selectedFire?.title || 'Информация о пожаре' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup color="white" />
        </q-card-section>

        <q-card-section v-if="selectedFire" class="q-pt-md">
          <div class="bg-orange-8 text-white q-pa-md q-mb-md rounded-borders text-center text-weight-bold">
            {{ getRiskLabel(selectedFire.severity) }}
          </div>

          <div class="row q-col-gutter-md">
            <div class="col-6">
              <div class="text-grey-4">Координаты</div>
              <div class="text-white text-weight-medium">{{ selectedFire.latitude.toFixed(3) }}, {{ selectedFire.longitude.toFixed(3) }}</div>
            </div>
            <div class="col-6">
              <div class="text-grey-4">Регион</div>
              <div class="text-white text-weight-medium">{{ selectedFire.region }}</div>
            </div>
          </div>



          <div class="row q-col-gutter-md q-mt-md">
            <div class="col-6">
              <div class="text-grey-4">Тип события</div>
              <div class="text-white text-weight-medium">{{ selectedFire.event_type === 'fire_started' ? 'Начало пожара' : selectedFire.event_type === 'fire_extinguished' ? 'Пожар потушен' : selectedFire.event_type }}</div>
            </div>
            <div class="col-6">
              <div class="text-grey-4">Дата события</div>
              <div class="text-white text-weight-medium">{{ formatDate(selectedFire.timestamp) }}</div>
            </div>
          </div>

          <div class="q-mt-md">
            <div class="text-grey-4">Описание</div>
            <div class="text-white">{{ selectedFire.description }}</div>
          </div>
        </q-card-section>

        <q-card-actions align="center" class="q-pa-md">
          <q-btn flat label="ПОДРОБНЕЕ" color="blue-5" class="q-px-md" icon="visibility" @click="viewFireDetails" />
          <q-btn flat label="МАРШРУТ" color="teal-5" class="q-px-md" icon="directions" @click="getDirections" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useQuasar } from 'quasar';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

const $q = useQuasar();

const searchQuery = ref('');
const riskLevel = ref({ label: 'Все уровни', value: 'all' });
const selectedRegion = ref({ label: 'Все регионы', value: 'all' });
const timeRange = ref({ label: 'Все время', value: 'all' });
const fireDetailsDialog = ref(false);
const selectedFire = ref(null);

const riskLevels = [
  { label: 'Все уровни', value: 'all' },
  { label: 'Низкий', value: 'low' },
  { label: 'Средний', value: 'medium' },
  { label: 'Высокий', value: 'high' },
  { label: 'Критический', value: 'critical' }
];

const regionOptions = [
  { label: 'Все регионы', value: 'all' },
  { label: 'Красноярский край', value: 'Красноярский край' },
  { label: 'Иркутская область', value: 'Иркутская область' },
  { label: 'Республика Саха', value: 'Республика Саха' },
  { label: 'Хабаровский край', value: 'Хабаровский край' },
  { label: 'Амурская область', value: 'Амурская область' },
  { label: 'Забайкальский край', value: 'Забайкальский край' },
  { label: 'Приморский край', value: 'Приморский край' },
  { label: 'Республика Бурятия', value: 'Республика Бурятия' },
  { label: 'Еврейская автономная область', value: 'Еврейская автономная область' }
];

const timeRanges = [
  { label: 'Все время', value: 'all' },
  { label: 'Последние 24 часа', value: '24h' },
  { label: 'Последние 7 дней', value: '7d' },
  { label: 'Последние 30 дней', value: '30d' },
  { label: 'Последние 3 месяца', value: '3m' },
  { label: 'Последние 6 месяцев', value: '6m' },
  { label: 'Последний год', value: '1y' }
];


const legendItems = [
  { label: 'Низкий риск', class: 'bg-green' },
  { label: 'Средний риск', class: 'bg-yellow' },
  { label: 'Высокий риск', class: 'bg-red' },
  { label: 'Критический риск', class: 'bg-purple' },
  { label: 'Потушенный пожар', class: 'extinguished-fire' }
];


const fireEvents = ref([]);
const fireStats = ref({
  total: 0,
  active: 0,
  critical: 0,
  extinguished: 0
});

let map = null;
let markers = L.layerGroup();
let regionsLayer = L.layerGroup();
// let heatLayer = null; // не используется
let resizeObserver = null;
let markerClusterGroup = null; // Добавляем кластеризацию
let rosleshozLayer = null; // layer for Rosleshoz observations
let predictionsClusterGroup = null; // кластеры предсказаний
let predictionsRefreshTimer = null;

function getRegionColor(riskLevel) {
  switch (riskLevel) {
    case 'low': return 'green';
    case 'medium': return 'yellow';
    case 'high': return 'red';
    case 'critical': return 'purple';
    default: return 'grey';
  }
}

function getRiskLevelText(riskLevel) {
  switch (riskLevel) {
    case 'low': return 'Низкий';
    case 'medium': return 'Средний';
    case 'high': return 'Высокий';
    case 'critical': return 'Критический';
    default: return 'Неизвестно';
  }
}

function getRiskLabel(riskLevel) {
  switch (riskLevel) {
    case 'low': return 'Низкий риск';
    case 'medium': return 'Средний риск';
    case 'high': return 'Высокий риск';
    case 'critical': return 'Критический риск';
    default: return 'Неизвестный уровень';
  }
}



function centerMapOnCurrentLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        map.setView([latitude, longitude], 10);

        L.marker([latitude, longitude], {
          icon: L.divIcon({
            className: 'current-location-marker',
            html: '<div class="pulse"></div>',
            iconSize: [20, 20]
          })
        }).addTo(map);
      },
      (error) => {
        console.error('Error getting location:', error);
        $q.notify({
          color: 'negative',
          message: 'Не удалось определить ваше местоположение',
          icon: 'error'
        });
      }
    );
  } else {
    $q.notify({
      color: 'negative',
      message: 'Геолокация не поддерживается вашим браузером',
      icon: 'error'
    });
  }
}

function zoomIn() {
  if (map) {
    map.setZoom(map.getZoom() + 1);
  }
}

function zoomOut() {
  if (map) {
    map.setZoom(map.getZoom() - 1);
  }
}

function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function formatOnlyDate(value) {
  if (!value) return '';
  const d = new Date(value);
  if (isNaN(d.getTime())) return '';
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${dd}.${mm}.${yyyy}`;
}

function formatPercent(v) {
  const n = Number(v);
  if (!isFinite(n)) return '0.0';
  return (Math.round(n * 10) / 10).toFixed(1);
}

function viewFireDetails() {
  fireDetailsDialog.value = false;
  $q.notify({
    color: 'info',
    message: 'Переход к подробной информации о пожаре',
    icon: 'info'
  });
  // Здесь можно добавить переход на страницу с подробной информацией
  // $router.push(`/fire-details/${selectedFire.value.id}`);
}

function getDirections() {
  if (selectedFire.value) {
    const { latitude, longitude } = selectedFire.value;
    const url = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`;
    window.open(url, '_blank');
    $q.notify({
      color: 'positive',
      message: 'Открытие маршрута в Google Maps',
      icon: 'directions'
    });
  }
}

// Улучшенное создание зон с адаптивным радиусом в зависимости от зума
function createDynamicZones(fireEvents) {
  console.log('Создаем динамические зоны на основе', fireEvents.length, 'пожаров');
  
  if (fireEvents.length === 0) return [];
  
  const currentZoom = map ? map.getZoom() : 5;
  
  // Адаптивный радиус зоны в зависимости от зума
  // На низком зуме - большие зоны, на высоком - маленькие
  let zoneRadius;
  if (currentZoom <= 4) {
    zoneRadius = 8; // Очень большие зоны для низкого зума
  } else if (currentZoom <= 6) {
    zoneRadius = 4; // Большие зоны для среднего зума
  } else if (currentZoom <= 8) {
    zoneRadius = 2; // Средние зоны для высокого зума
  } else {
    zoneRadius = 1; // Маленькие зоны для очень высокого зума
  }
  
  console.log(`Текущий зум: ${currentZoom}, радиус зоны: ${zoneRadius} градусов`);
  
  // Используем алгоритм кластеризации для группировки близких точек
  const zones = new Map();
  const processedEvents = new Set();
  
  fireEvents.forEach(event => {
    if (!event.latitude || !event.longitude || processedEvents.has(event.id)) return;
    
    // Создаем новую зону с этим событием как центром
    const zoneId = `zone_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
         const zone = {
       id: zoneId,
       center: [event.latitude, event.longitude],
       fires: [event],
       totalRisk: getRiskScore(event.severity),
       maxSeverity: event.severity,
       bounds: calculateZoneBounds([event.latitude, event.longitude], zoneRadius)
     };
    
    zones.set(zoneId, zone);
    processedEvents.add(event.id);
    
    // Ищем все события в радиусе этой зоны и добавляем их
    fireEvents.forEach(otherEvent => {
      if (!otherEvent.latitude || !otherEvent.longitude || processedEvents.has(otherEvent.id)) return;
      
      const distance = Math.sqrt(
        Math.pow(event.latitude - otherEvent.latitude, 2) + 
        Math.pow(event.longitude - otherEvent.longitude, 2)
      );
      
             if (distance <= zoneRadius) {
         zone.fires.push(otherEvent);
         zone.totalRisk += getRiskScore(otherEvent.severity);
         zone.maxSeverity = getMaxSeverity(zone.maxSeverity, otherEvent.severity);
         processedEvents.add(otherEvent.id);
       }
    });
  });
  
  // Преобразуем зоны в массив и рассчитываем статистику
  const result = Array.from(zones.values()).map(zone => {
    const avgRisk = zone.totalRisk / zone.fires.length;
    const riskLevel = getRiskLevelFromScore(avgRisk);
    
    return {
      ...zone,
      fireCount: zone.fires.length,
      riskLevel: riskLevel,
      density: zone.fires.length / calculateZoneArea(zone.bounds),
      // Создаем полигон для зоны с адаптивным радиусом
      polygon: createZonePolygon(zone.center, zoneRadius, riskLevel)
    };
  });
  
  console.log(`Создано ${result.length} зон с адаптивным радиусом`);
  return result;
}

// Вспомогательные функции
function getRiskScore(severity) {
  switch (severity) {
    case 'low': return 1;
    case 'medium': return 2;
    case 'high': return 3;
    case 'critical': return 4;
    default: return 1;
  }
}

function getMaxSeverity(current, newSeverity) {
  const severityOrder = ['low', 'medium', 'high', 'critical'];
  const currentIndex = severityOrder.indexOf(current);
  const newIndex = severityOrder.indexOf(newSeverity);
  return newIndex > currentIndex ? newSeverity : current;
}

function getRiskLevelFromScore(score) {
  if (score >= 3.5) return 'critical';
  if (score >= 2.5) return 'high';
  if (score >= 1.5) return 'medium';
  return 'low';
}

function calculateZoneBounds(center, radius) {
  return {
    north: center[0] + radius,
    south: center[0] - radius,
    east: center[1] + radius,
    west: center[1] - radius
  };
}

function calculateZoneArea(bounds) {
  const latDiff = bounds.north - bounds.south;
  const lonDiff = bounds.east - bounds.west;
  return latDiff * lonDiff;
}

function createZonePolygon(center, radius, riskLevel) {
  // Создаем круглый полигон для зоны
  const points = [];
  const segments = 16;
  
  for (let i = 0; i < segments; i++) {
    const angle = (i / segments) * 2 * Math.PI;
    const lat = center[0] + radius * Math.cos(angle);
    const lng = center[1] + radius * Math.sin(angle);
    points.push([lat, lng]);
  }
  
  return {
    coordinates: points,
    riskLevel: riskLevel,
    center: center
  };
}

// Обновленная функция добавления зон на карту
function addDynamicZonesToMap(zones) {
  regionsLayer.clearLayers();
  
  const currentZoom = map.getZoom();
  
  // Показываем зоны только на среднем и низком зуме (3-8)
  if (currentZoom >= 3 && currentZoom <= 8) {
    console.log('Добавляем', zones.length, 'динамических зон на карту');
    
    zones.forEach(zone => {
      if (zone.polygon) {
        const polygon = L.polygon(zone.polygon.coordinates, {
          color: getRegionColor(zone.riskLevel),
          fillColor: getRegionColor(zone.riskLevel),
          fillOpacity: Math.min(0.3, 0.1 + (zone.fireCount * 0.02)), // Прозрачность зависит от количества пожаров
          weight: 2,
          interactive: true
        });
        
        // Добавляем всплывающую подсказку
        polygon.bindPopup(`
          <div style="min-width: 200px;">
            <h4 style="margin: 0 0 8px 0; color: ${getRegionColor(zone.riskLevel)};">
              Зона пожаров
            </h4>
            <p><strong>Количество пожаров:</strong> ${zone.fireCount}</p>
            <p><strong>Уровень риска:</strong> ${getRiskLevelText(zone.riskLevel)}</p>
            <p><strong>Максимальная серьезность:</strong> ${getRiskLevelText(zone.maxSeverity)}</p>
            <p><strong>Плотность:</strong> ${zone.density.toFixed(2)} пожаров/км²</p>
          </div>
        `);
        
        polygon.addTo(regionsLayer);
      }
    });
  }
}

// Загружаем данные только из API
async function loadFireEvents() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/fire-events?limit=200');
    if (response.ok) {
      const events = await response.json();
      console.log('Загружено событий:', events.length);
      return events;
    } else {
      console.error('Ошибка загрузки данных с API:', response.status, response.statusText);
      throw new Error(`API error: ${response.status}`);
    }
  } catch (error) {
    console.error('Error loading fire events:', error);
    throw error;
  }
}



function refreshMap() {
  $q.loading.show({
    message: 'Обновление данных...'
  });

  loadFireEvents().then(events => {
    fireEvents.value = events;
    
    // Создаем динамические зоны
    const dynamicZones = createDynamicZones(events);
    console.log('Создано динамических зон:', dynamicZones.length);
    
    addMarkersToMap(events);
    addDynamicZonesToMap(dynamicZones);

    $q.loading.hide();
    $q.notify({
      color: 'positive',
      message: 'Данные обновлены',
      icon: 'update'
    });
  }).catch(error => {
    console.error('Error refreshing map:', error);
    $q.loading.hide();
    $q.notify({
      color: 'negative',
      message: `Ошибка загрузки данных: ${error.message}`,
      icon: 'error'
    });
  });
}

function applyFilters() {
  $q.loading.show({
    message: 'Применение фильтров...'
  });

  const filteredEvents = [...fireEvents.value].filter(event => {
    // Фильтр по уровню риска
    if (riskLevel.value.value !== 'all' && event.severity !== riskLevel.value.value) {
      return false;
    }

    // Фильтр по региону
    if (selectedRegion.value.value !== 'all' && event.region !== selectedRegion.value.value) {
      return false;
    }

    // Фильтр по поисковому запросу
    if (searchQuery.value && !event.region?.toLowerCase().includes(searchQuery.value.toLowerCase())) {
      return false;
    }

    // Фильтр по временному диапазону
    if (timeRange.value.value !== 'all') {
      const eventDate = new Date(event.timestamp);
      const now = new Date();
      const timeDiff = now - eventDate;
      
      let maxTimeDiff;
      switch (timeRange.value.value) {
        case '24h':
          maxTimeDiff = 24 * 60 * 60 * 1000; // 24 часа
          break;
        case '7d':
          maxTimeDiff = 7 * 24 * 60 * 60 * 1000; // 7 дней
          break;
        case '30d':
          maxTimeDiff = 30 * 24 * 60 * 60 * 1000; // 30 дней
          break;
        case '3m':
          maxTimeDiff = 3 * 30 * 24 * 60 * 60 * 1000; // 3 месяца
          break;
        case '6m':
          maxTimeDiff = 6 * 30 * 24 * 60 * 60 * 1000; // 6 месяцев
          break;
        case '1y':
          maxTimeDiff = 365 * 24 * 60 * 60 * 1000; // 1 год
          break;
        default:
          maxTimeDiff = Infinity;
      }
      
      if (timeDiff > maxTimeDiff) {
        return false;
      }
    }

    return true;
  });

  addMarkersToMap(filteredEvents);
  addDynamicZonesToMap(createDynamicZones(filteredEvents)); // Применяем фильтры к зонам

  fireStats.value = {
    total: filteredEvents.length,
    active: filteredEvents.filter(e => e.event_type === 'fire_started').length,
    critical: filteredEvents.filter(e => e.severity === 'critical').length,
    extinguished: filteredEvents.filter(e => e.event_type === 'fire_extinguished').length
  };

  $q.loading.hide();
}

function addMarkersToMap(events) {
  markers.clearLayers();
  
  // Создаем кластерную группу для лучшей производительности
  if (markerClusterGroup) {
    map.removeLayer(markerClusterGroup);
  }
  
  markerClusterGroup = L.markerClusterGroup({
    chunkedLoading: true,
    maxClusterRadius: 50,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    zoomToBoundsOnClick: true,
    disableClusteringAtZoom: 12, // Отключаем кластеризацию на высоком зуме
    iconCreateFunction: function(cluster) {
      const count = cluster.getChildCount();
      let className = 'marker-cluster-small';
      let size = 40;
      
      if (count > 100) {
        className = 'marker-cluster-large';
        size = 60;
      } else if (count > 10) {
        className = 'marker-cluster-medium';
        size = 50;
      }
      
      return L.divIcon({
        html: `<div><span>${count}</span></div>`,
        className: `marker-cluster ${className}`,
        iconSize: L.point(size, size)
      });
    }
  });

  events.forEach(event => {
    let color = 'green';
    if (event.severity === 'medium') color = 'orange';
    if (event.severity === 'high') color = 'red';
    if (event.severity === 'critical') color = 'purple';
    
    // Для потушенных пожаров используем серый цвет
    if (event.event_type === 'fire_extinguished') color = 'grey';

    const marker = L.circleMarker([event.latitude, event.longitude], {
      radius: event.severity === 'critical' ? 12 :
        event.severity === 'high' ? 10 :
          event.severity === 'medium' ? 8 : 6,
      fillColor: color,
      color: 'white',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8,
      interactive: true,
      bubblingMouseEvents: false,
      className: (event.severity === 'critical' || event.severity === 'high') && event.event_type !== 'fire_extinguished' ? 'fire-marker' : '',
      pane: 'markerPane'
    });

    marker.on('click', () => {
      console.log('Marker clicked:', event);
      try {
        selectedFire.value = event;
        fireDetailsDialog.value = true;
        console.log('Dialog opened for fire:', event.title);
      } catch (error) {
        console.error('Error opening fire dialog:', error);
        $q.notify({
          color: 'negative',
          message: 'Ошибка при открытии информации о пожаре',
          icon: 'error'
        });
      }
    });

    markerClusterGroup.addLayer(marker);
  });

  map.addLayer(markerClusterGroup);

  // Rosleshoz observations layer
  if (!rosleshozLayer) {
    rosleshozLayer = L.layerGroup().addTo(map);
  }

  // Инициализируем кластер предсказаний
  if (!predictionsClusterGroup) {
    predictionsClusterGroup = L.markerClusterGroup({
      chunkedLoading: true,
      maxClusterRadius: 50,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      disableClusteringAtZoom: 12
    });
    map.addLayer(predictionsClusterGroup);
  }
}


// === Предсказания (новые и старые) ===
async function loadPredictionMarkers() {
  try {
    const list = await fetch('http://localhost:8000/api/v1/predictions/history?limit=500')
      .then(r => r.ok ? r.json() : []);

    // очистить прошлые
    if (predictionsClusterGroup) {
      predictionsClusterGroup.clearLayers();
    }

    list.forEach(p => {
      const lat = p.latitude;
      const lng = p.longitude;
      const level = p.risk_level;
      let color = 'green';
      if (level === 'medium') color = 'orange';
      if (level === 'high') color = 'red';
      if (level === 'critical') color = 'purple';

      const marker = L.circleMarker([lat, lng], {
        radius: level === 'critical' ? 12 : level === 'high' ? 10 : 8,
        fillColor: color,
        color: 'white',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9,
        interactive: true,
        bubblingMouseEvents: false,
        className: level === 'critical' || level === 'high' ? 'fire-marker' : ''
      });

      marker.bindPopup(`
        <div style="min-width: 200px;">
          <h4 style="margin: 0 0 8px 0; color: ${color};">Предсказание</h4>
          <p><strong>Дата прогноза:</strong> ${formatOnlyDate(p.created_at)}</p>
          <p><strong>Риск:</strong> ${getRiskLabel(level)}</p>
          <p><strong>Вероятность:</strong> ${formatPercent(p.risk_percentage)}%</p>
          <p><strong>Уверенность:</strong> ${formatPercent(p.confidence)}%</p>
        </div>
      `);

      predictionsClusterGroup.addLayer(marker);
    });
  } catch (e) {
    console.error('Failed to load prediction markers', e);
  }
}



// Обновляем обработчик изменения зума
function onZoomEnd() {
  const currentZoom = map.getZoom();
  console.log('Zoom изменился на:', currentZoom);
  
  // Обновляем отображение в зависимости от зума
  if (currentZoom >= 9) {
    // На высоком зуме показываем только точки
    regionsLayer.clearLayers();
  } else if (currentZoom >= 3 && currentZoom <= 8) {
    // На среднем зуме пересчитываем зоны с новым радиусом
    console.log('Пересчитываем зоны для зума:', currentZoom);
    addDynamicZonesToMap(createDynamicZones(fireEvents.value));
  } else {
    // На очень низком зуме очищаем зоны
    regionsLayer.clearLayers();
  }
  
  // Обновляем кластеризацию
  if (markerClusterGroup) {
    markerClusterGroup.refreshClusters();
  }
}

onMounted(async () => {
  try {
    console.log('Initializing map page...');
    
    await nextTick();
    
    const mapContainer = document.getElementById('risk-map');
    if (!mapContainer) {
      console.error('Map container not found!');
      return;
    }
    
    console.log('Map container found:', mapContainer);
    console.log('Container dimensions:', mapContainer.offsetWidth, 'x', mapContainer.offsetHeight);
    
    map = L.map('risk-map', {
      zoomControl: true,
      attributionControl: false
    }).setView([61.5240, 105.3188], 3);

    console.log('Map created successfully');

    const baseLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
      attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
      maxZoom: 18,
      minZoom: 3
    }).addTo(map);

    const fallbackLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      subdomains: 'abc',
      maxZoom: 18,
      minZoom: 3
    });

    baseLayer.on('tileerror', function() {
      console.log('Основной слой недоступен, переключаемся на альтернативный');
      map.removeLayer(baseLayer);
      fallbackLayer.addTo(map);
    });

    console.log('Base layer added');

    markers = L.layerGroup().addTo(map);
    console.log('Markers layer added');
    regionsLayer = L.layerGroup().addTo(map);
    console.log('Regions layer added');

    // Добавляем обработчик изменения зума
    map.on('zoomend', onZoomEnd);

    try {
      const events = await loadFireEvents();
      fireEvents.value = events;
      console.log('Fire events loaded:', events.length);
      
             // Обновляем статистику
       fireStats.value = {
         total: events.length,
         active: events.filter(e => e.event_type === 'fire_started').length,
         critical: events.filter(e => e.severity === 'critical').length,
         extinguished: events.filter(e => e.event_type === 'fire_extinguished').length
       };
      
      addMarkersToMap(events);
      addDynamicZonesToMap(createDynamicZones(events)); // Загружаем зоны при инициализации
      console.log('Markers and regions added to map');
    } catch (error) {
      console.error('Error loading fire events:', error);
      $q.notify({
        color: 'negative',
        message: `Ошибка загрузки данных: ${error.message}`,
        icon: 'error'
      });
    }

    resizeObserver = new ResizeObserver(() => {
      if (map) {
        setTimeout(() => {
          map.invalidateSize();
          console.log('Map resized and invalidated');
        }, 100);
      }
    });

    resizeObserver.observe(mapContainer);

    setTimeout(() => {
      if (map) {
        map.invalidateSize();
        console.log('Map size updated');
        console.log('Map container size after invalidate:', mapContainer.offsetWidth, 'x', mapContainer.offsetHeight);
      }
    }, 1000);

    // Первичная отрисовка предсказаний
    await loadPredictionMarkers();

    // Периодическое обновление предсказаний
    predictionsRefreshTimer = setInterval(loadPredictionMarkers, 30000);

    // Load Rosleshoz observations and refresh periodically
    async function loadRosleshoz() {
      try {
        const data = await fetch('http://localhost:8000/api/v1/data/rosleshoz/operative').then(r => r.json());
        if (rosleshozLayer) rosleshozLayer.clearLayers();
        const pts = data.region_points || [];
        pts.forEach(p => {
          const m = L.circleMarker([p.latitude, p.longitude], {
            radius: 6,
            color: 'white',
            weight: 1,
            fillColor: '#00bcd4',
            fillOpacity: 0.9
          });
          m.bindPopup(`<div><strong>${p.name}</strong><br/>Источник: Рослесхоз<br/>Дата: ${data.bulletin_date || ''}</div>`);
          rosleshozLayer.addLayer(m);
        });
      } catch { /* ignore */ }
    }
    await loadRosleshoz();
    setInterval(loadRosleshoz, 30 * 60 * 1000);

    console.log('Map initialization completed');
    
  } catch (error) {
    console.error('Error initializing map:', error);
  }
});

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect();
    resizeObserver = null;
  }
  
  if (map) {
    map.remove();
    map = null;
  }
  if (predictionsRefreshTimer) {
    clearInterval(predictionsRefreshTimer);
    predictionsRefreshTimer = null;
  }
});
</script>

<style lang="scss" scoped>
.map-page {
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

.map-container {
  width: 100%;
  height: 100%;
  min-height: 600px;
}

.map-card {
  height: 100%;
  min-height: 600px;
  display: flex;
  flex-direction: column;
  
  .card-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0 !important;
  }
  
  &.full-height {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
}

@media (max-width: 1023px) {
  .map-card.full-height {
    height: 500px;
  }
}

@media (max-width: 768px) {
  .map-card.full-height {
    height: 350px;
  }
}

#risk-map {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.leaflet-container) {
  border-radius: 8px;
  background-color: #1a202c;
  width: 100%;
  height: 100%;
}

:deep(.leaflet-tile) {
  filter: brightness(0.9) contrast(1.1);
}

:deep(.leaflet-control-attribution) {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 10px;
}

:deep(.leaflet-control-zoom) {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  border: none;
}

:deep(.leaflet-control-zoom-in),
:deep(.leaflet-control-zoom-out) {
  background-color: rgba(30, 41, 59, 0.9) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  transition: all 0.2s ease;

  &:hover {
    background-color: rgba(59, 130, 246, 0.8) !important;
    transform: scale(1.05);
  }
}

:deep(.leaflet-marker-icon) {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

@keyframes fire-pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
  }

  70% {
    box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
  }

  100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
  }
}

:deep(.fire-marker) {
  animation: fire-pulse 2s infinite;
}

:deep(.leaflet-marker-pane) {
  z-index: 600 !important;
}

:deep(.leaflet-overlay-pane) {
  z-index: 400 !important;
}

.fire-info-modal {
  min-width: 300px;
  border-radius: 12px;
}

.legend-over-map {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.legend-item {
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.05);
  }
}

.map-controls {
  z-index: 1000;
  
  .control-btn {
    transition: all 0.2s ease;
    
    &:hover {
      background: rgba(37, 99, 235, 0.1);
      transform: scale(1.1);
    }
  }
}

.legend-indicator {
  width: 20px;
  height: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.bg-green {
  background: linear-gradient(135deg, #22c55e, #16a34a);
}

.bg-yellow {
  background: linear-gradient(135deg, #eab308, #ca8a04);
}

.bg-orange {
  background: linear-gradient(135deg, #f97316, #ea580c);
}

.bg-red {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.bg-purple {
  background: linear-gradient(135deg, #a855f7, #9333ea);
}

.active-fire {
  background: radial-gradient(circle, #ff5252 0%, #ff0000 100%);
  box-shadow: 0 0 8px #ff0000;
}

.extinguished-fire {
  background: #607d8b;
  border: 1px dashed #455a64;
}

.regions-list {
  .region-item {
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

  .region-avatar {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .risk-badge {
    font-weight: 600;
    border-radius: 8px;
  }
}

.legend-item {
  padding: 12px;
  border-radius: 8px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(37, 99, 235, 0.05);
    transform: translateX(2px);
  }
}

.stat-item {
  padding: 16px;
  border-radius: 12px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(37, 99, 235, 0.05);
    transform: translateY(-2px);
  }
}

.fire-details-dialog {
  .risk-badge {
    font-weight: 600;
    border-radius: 8px;
  }
}

.current-location-marker {
  .pulse {
    width: 20px;
    height: 20px;
    background-color: rgba(38, 198, 218, 0.7);
    border-radius: 50%;
    box-shadow: 0 0 0 rgba(38, 198, 218, 0.4);
    animation: pulse 2s infinite;
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(38, 198, 218, 0.7);
  }

  70% {
    box-shadow: 0 0 0 15px rgba(38, 198, 218, 0);
  }

  100% {
    box-shadow: 0 0 0 0 rgba(38, 198, 218, 0);
  }
}

body.body--dark {
  :deep(.leaflet-tile) {
    filter: brightness(0.8) contrast(1.2) saturate(0.8);
  }

  :deep(.leaflet-popup-content-wrapper) {
    background-color: #1e293b;
    color: #f8fafc;
  }

  :deep(.leaflet-popup-tip) {
    background-color: #1e293b;
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .map-container {
    height: 400px;
  }
  
  .page-header {
    padding: 1rem 0;
    
    .text-h4 {
      font-size: 1.75rem;
    }
  }
}

// Стили для кластеров маркеров
:deep(.marker-cluster) {
  background: rgba(37, 99, 235, 0.8);
  border: 2px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  color: white;
  font-weight: bold;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(37, 99, 235, 1);
    transform: scale(1.1);
  }
  
  span {
    font-size: 12px;
    font-weight: 600;
  }
}

:deep(.marker-cluster-small) {
  background: rgba(34, 197, 94, 0.8);
  
  &:hover {
    background: rgba(34, 197, 94, 1);
  }
}

:deep(.marker-cluster-medium) {
  background: rgba(245, 158, 11, 0.8);
  
  &:hover {
    background: rgba(245, 158, 11, 1);
  }
}

:deep(.marker-cluster-large) {
  background: rgba(239, 68, 68, 0.8);
  
  &:hover {
    background: rgba(239, 68, 68, 1);
  }
}
</style>