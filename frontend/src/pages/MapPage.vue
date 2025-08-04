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
              <div class="col-12 col-md-4">
                <q-input outlined dense v-model="searchQuery" label="Поиск по региону" clearable class="search-input"
                  @update:model-value="applyFilters">
                  <template v-slot:append>
                    <q-icon name="search" />
                  </template>
                </q-input>
              </div>
              <div class="col-12 col-md-4">
                <q-select outlined dense v-model="riskLevel" :options="riskLevels" label="Уровень риска"
                  @update:model-value="applyFilters" />
              </div>
              <div class="col-12 col-md-4">
                <q-select outlined dense v-model="timeRange" :options="timeRanges" label="Временной диапазон"
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
            <q-list separator class="regions-list">
              <q-item v-for="(region, index) in topRiskRegions" :key="index" clickable @click="centerMapOn(region)"
                class="region-item">
                <q-item-section avatar>
                  <q-avatar :color="getRegionColor(region.riskLevel)" text-color="white" class="region-avatar">
                    {{ index + 1 }}
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-medium">{{ region.name }}</q-item-label>
                  <q-item-label caption>
                    <span class="text-weight-medium">{{ region.activeFires }}</span> активных пожаров
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-badge :color="getRegionColor(region.riskLevel)" class="risk-badge">
                    {{ getRiskLevelText(region.riskLevel) }}
                  </q-badge>
                </q-item-section>
              </q-item>
            </q-list>
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
            {{ getRiskLabel(selectedFire.risk_level) }}
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
              <div class="text-grey-4">Температура</div>
              <div class="text-white text-weight-medium">{{ selectedFire.temperature }}°C</div>
            </div>
            <div class="col-6">
              <div class="text-grey-4">Влажность</div>
              <div class="text-white text-weight-medium">{{ selectedFire.humidity }}%</div>
            </div>
          </div>

          <div class="row q-col-gutter-md q-mt-md">
            <div class="col-6">
              <div class="text-grey-4">Статус</div>
              <div class="text-white text-weight-medium">{{ selectedFire.status === 'active' ? 'Активный' : 'Потухший' }}</div>
            </div>
            <div class="col-6">
              <div class="text-grey-4">Дата обнаружения</div>
              <div class="text-white text-weight-medium">{{ formatDate(selectedFire.created_at) }}</div>
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

const $q = useQuasar();

const searchQuery = ref('');
const riskLevel = ref({ label: 'Все уровни', value: 'all' });
const timeRange = ref({ label: 'Текущая ситуация', value: 'current' });
const fireDetailsDialog = ref(false);
const selectedFire = ref(null);

const riskLevels = [
  { label: 'Все уровни', value: 'all' },
  { label: 'Низкий', value: 'low' },
  { label: 'Средний', value: 'medium' },
  { label: 'Высокий', value: 'high' },
  { label: 'Критический', value: 'critical' }
];

const timeRanges = [
  { label: 'Текущая ситуация', value: 'current' },
  { label: 'Прогноз на 24 часа', value: '24h' },
  { label: 'Прогноз на 3 дня', value: '3d' },
  { label: 'Прогноз на 7 дней', value: '7d' }
];

const legendItems = [
  { label: 'Низкий риск', class: 'bg-green' },
  { label: 'Средний риск', class: 'bg-yellow' },
  { label: 'Высокий риск', class: 'bg-red' },
  { label: 'Критический риск', class: 'bg-purple' },
  { label: 'Потушенный пожар', class: 'extinguished-fire' }
];

const topRiskRegions = ref([]);
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
let heatLayer = null;
let resizeObserver = null;

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

function centerMapOn(region) {
  if (map && region.coords) {
    map.setView(region.coords, 6);
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

async function loadFireEvents() {
  try {
    // Временно используем мок-данные вместо API
    const mockEvents = [
      {
        id: 1,
        title: 'Пожар в Красноярском крае',
        description: 'Лесной пожар в районе Красноярска',
        latitude: 56.0184,
        longitude: 92.8672,
        risk_level: 'high',
        status: 'active',
        region: 'Красноярский край',
        temperature: 28,
        humidity: 45,
        created_at: '2024-01-15T10:30:00Z'
      },
      {
        id: 2,
        title: 'Пожар в Иркутской области',
        description: 'Критическая ситуация с пожаром',
        latitude: 52.2864,
        longitude: 104.3050,
        risk_level: 'critical',
        status: 'active',
        region: 'Иркутская область',
        temperature: 32,
        humidity: 30,
        created_at: '2024-01-15T09:15:00Z'
      },
      {
        id: 3,
        title: 'Пожар в Республике Саха',
        description: 'Пожар в лесной зоне',
        latitude: 66.2654,
        longitude: 129.6755,
        risk_level: 'medium',
        status: 'active',
        region: 'Республика Саха',
        temperature: 25,
        humidity: 60,
        created_at: '2024-01-15T08:45:00Z'
      },
      {
        id: 4,
        title: 'Пожар в Московской области',
        description: 'Небольшой пожар в лесу',
        latitude: 55.7558,
        longitude: 37.6173,
        risk_level: 'low',
        status: 'active',
        region: 'Московская область',
        temperature: 22,
        humidity: 65,
        created_at: '2024-01-15T07:30:00Z'
      },
      {
        id: 5,
        title: 'Потушенный пожар в Ленинградской области',
        description: 'Пожар был потушен',
        latitude: 59.9311,
        longitude: 30.3609,
        risk_level: 'medium',
        status: 'extinguished',
        region: 'Ленинградская область',
        temperature: 20,
        humidity: 70,
        created_at: '2024-01-14T15:20:00Z'
      }
    ];

    fireEvents.value = mockEvents;

    fireStats.value = {
      total: fireEvents.value.length,
      active: fireEvents.value.filter(e => e.status === 'active').length,
      critical: fireEvents.value.filter(e => e.risk_level === 'critical').length,
      extinguished: fireEvents.value.filter(e => e.status !== 'active').length
    };

    return mockEvents;
  } catch (error) {
    console.error('Error loading fire events:', error);
    return [];
  }
}

async function loadHighRiskRegions() {
  try {
    // Временно используем мок-данные вместо API
    const mockRegions = [
      {
        id: 1,
        name: 'Красноярский край',
        risk_level: 'high',
        active_fires: 5,
        coords: [56.0184, 92.8672]
      },
      {
        id: 2,
        name: 'Иркутская область',
        risk_level: 'critical',
        active_fires: 8,
        coords: [52.2864, 104.3050]
      },
      {
        id: 3,
        name: 'Республика Саха',
        risk_level: 'medium',
        active_fires: 3,
        coords: [66.2654, 129.6755]
      },
      {
        id: 4,
        name: 'Амурская область',
        risk_level: 'high',
        active_fires: 4,
        coords: [50.2904, 127.5272]
      },
      {
        id: 5,
        name: 'Хабаровский край',
        risk_level: 'medium',
        active_fires: 2,
        coords: [48.4802, 135.0719]
      }
    ];

    topRiskRegions.value = mockRegions;
  } catch (error) {
    console.error('Error loading high risk regions:', error);
  }
}

function refreshMap() {
  $q.loading.show({
    message: 'Обновление данных...'
  });

  Promise.all([
    loadFireEvents(),
    loadHighRiskRegions()
  ]).then(([events]) => {
    markers.clearLayers();
    regionsLayer.clearLayers(); // Очищаем полигоны

    addMarkersToMap(events);
    addRegionsToMap(topRiskRegions.value); // Добавляем полигоны

    $q.loading.hide();
    $q.notify({
      color: 'positive',
      message: 'Данные обновлены',
      icon: 'update'
    });
  }).catch(() => {
    $q.loading.hide();
  });
}

function applyFilters() {
  $q.loading.show({
    message: 'Применение фильтров...'
  });

  const filteredEvents = [...fireEvents.value].filter(event => {
    if (riskLevel.value.value !== 'all' && event.risk_level !== riskLevel.value.value) {
      return false;
    }

    if (searchQuery.value && !event.region?.toLowerCase().includes(searchQuery.value.toLowerCase())) {
      return false;
    }

    return true;
  });

  markers.clearLayers();
  regionsLayer.clearLayers(); // Очищаем полигоны при применении фильтров

  addMarkersToMap(filteredEvents);
  addRegionsToMap(topRiskRegions.value); // Добавляем полигоны после фильтрации

  fireStats.value = {
    total: filteredEvents.length,
    active: filteredEvents.filter(e => e.status === 'active').length,
    critical: filteredEvents.filter(e => e.risk_level === 'critical').length,
    extinguished: filteredEvents.filter(e => e.status !== 'active').length
  };

  $q.loading.hide();
}

function addMarkersToMap(events) {
  events.forEach(event => {
    let color = 'green';
    if (event.risk_level === 'medium') color = 'orange';
    if (event.risk_level === 'high') color = 'red';
    if (event.risk_level === 'critical') color = 'purple';
    
    // Для потушенных пожаров используем серый цвет
    if (event.status === 'extinguished') color = 'grey';

    const marker = L.circleMarker([event.latitude, event.longitude], {
      radius: event.risk_level === 'critical' ? 12 :
        event.risk_level === 'high' ? 10 :
          event.risk_level === 'medium' ? 8 : 6,
      fillColor: color,
      color: 'white',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.8,
      interactive: true,
      bubblingMouseEvents: false,
      className: (event.risk_level === 'critical' || event.risk_level === 'high') && event.status !== 'extinguished' ? 'fire-marker' : '',
      pane: 'markerPane' // Убеждаемся что маркеры в правильном слое
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

    markers.addLayer(marker);
  });

  if (heatLayer) {
    map.removeLayer(heatLayer);
  }

  const heatPoints = [];
  events.forEach(event => {
    heatPoints.push([event.latitude, event.longitude, event.risk_level === 'critical' ? 1.0 :
      event.risk_level === 'high' ? 0.8 :
        event.risk_level === 'medium' ? 0.6 : 0.4]);

    if (event.risk_level === 'high' || event.risk_level === 'critical') {
      for (let i = 0; i < 5; i++) {
        const lat = event.latitude + (Math.random() - 0.5) * 0.1;
        const lng = event.longitude + (Math.random() - 0.5) * 0.1;
        heatPoints.push([lat, lng, 0.3]);
      }
    }
  });

  markers.addTo(map);
}

function addRegionsToMap(regions) {
  const regionPolygons = {
    'Красноярский край': [
      [50.0, 90.0],
      [50.0, 100.0],
      [60.0, 100.0],
      [60.0, 90.0]
    ],
    'Иркутская область': [
      [50.0, 100.0],
      [50.0, 110.0],
      [60.0, 110.0],
      [60.0, 100.0]
    ],
    'Республика Саха (Якутия)': [
      [60.0, 110.0],
      [60.0, 130.0],
      [70.0, 130.0],
      [70.0, 110.0]
    ],
    'Забайкальский край': [
      [50.0, 110.0],
      [50.0, 120.0],
      [55.0, 120.0],
      [55.0, 110.0]
    ],
    'Амурская область': [
      [50.0, 120.0],
      [50.0, 130.0],
      [55.0, 130.0],
      [55.0, 120.0]
    ]
  };

  regions.forEach(region => {
    const coords = regionPolygons[region.name];
    if (coords) {
      L.polygon(coords, {
        color: getRegionColor(region.riskLevel),
        fillColor: getRegionColor(region.riskLevel),
        fillOpacity: 0.1, // Уменьшаем прозрачность
        weight: 1,
        interactive: false // Делаем полигоны неинтерактивными
      })
        .addTo(regionsLayer);
    }
  });
}

onMounted(async () => {
  try {
    console.log('Initializing map page...');
    
    // Небольшая задержка для правильной инициализации
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

    // Используем те же тайлы что и на главной странице
    const baseLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
      attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
      maxZoom: 18,
      minZoom: 3
    }).addTo(map);

    // Альтернативный слой на случай проблем с основным
    const fallbackLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      subdomains: 'abc',
      maxZoom: 18,
      minZoom: 3
    });

    // Проверяем загрузку основного слоя
    baseLayer.on('tileerror', function() {
      console.log('Основной слой недоступен, переключаемся на альтернативный');
      map.removeLayer(baseLayer);
      fallbackLayer.addTo(map);
    });

    console.log('Base layer added');

    markers = L.layerGroup().addTo(map);
    console.log('Markers layer added');
    regionsLayer = L.layerGroup().addTo(map); // Инициализируем слой полигонов
    console.log('Regions layer added');

    // Загружаем данные с обработкой ошибок
    try {
      await loadHighRiskRegions();
      console.log('Regions loaded');
    } catch (error) {
      console.error('Error loading regions:', error);
    }

    try {
      const events = await loadFireEvents();
      console.log('Fire events loaded:', events.length);
      addMarkersToMap(events);
      addRegionsToMap(topRiskRegions.value); // Добавляем полигоны после маркеров
      console.log('Markers and regions added to map');
    } catch (error) {
      console.error('Error loading fire events:', error);
    }

    // Добавляем ResizeObserver для автоматического обновления размера
    resizeObserver = new ResizeObserver(() => {
      if (map) {
        setTimeout(() => {
          map.invalidateSize();
          console.log('Map resized and invalidated');
        }, 100);
      }
    });

    resizeObserver.observe(mapContainer);

    // Обновляем размер карты
    setTimeout(() => {
      if (map) {
        map.invalidateSize();
        console.log('Map size updated');
        console.log('Map container size after invalidate:', mapContainer.offsetWidth, 'x', mapContainer.offsetHeight);
      }
    }, 1000);

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
</style>