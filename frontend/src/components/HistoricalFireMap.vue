<template>
  <div class="historical-fire-map">
    <q-card class="map-card">
      <q-card-section class="card-header">
        <div class="row items-center">
          <q-icon name="map" size="28px" color="red" class="q-mr-md" />
          <div>
            <div class="text-h6 text-weight-bold">Исторические пожары</div>
            <div class="text-caption text-grey-6">Карта всех зарегистрированных пожаров</div>
          </div>
        </div>
      </q-card-section>
      
      <q-card-section class="card-content">
                 <!-- Фильтры -->
         <div class="row q-col-gutter-md q-mb-lg">
           <div class="col-12 col-md-2">
             <q-select
               v-model="selectedYear"
               :options="yearOptions"
               outlined
               dense
               label="Год"
               @update:model-value="loadFireData"
             />
           </div>
           <div class="col-12 col-md-2">
             <q-select 
               outlined 
               dense 
               v-model="selectedSeverity" 
               :options="severityOptions" 
               label="Серьезность" 
               class="filter-input"
               @update:model-value="loadFireData"
             />
           </div>
           <div class="col-12 col-md-2">
             <q-select 
               outlined 
               dense 
               v-model="selectedRegion" 
               :options="regionOptions" 
               label="Регион" 
               class="filter-input"
               @update:model-value="loadFireData"
             />
           </div>
           <div class="col-12 col-md-2">
             <q-toggle
               v-model="showPolygons"
               label="Показывать полигоны"
               color="primary"
               @update:model-value="loadFireData"
             />
           </div>
           <div class="col-12 col-md-2">
             <q-input
               v-model.number="maxPoints"
               type="number"
               outlined
               dense
               label="Макс. точек"
               :min="100"
               :max="5000"
               @update:model-value="loadFireData"
             />
           </div>
           <div class="col-12 col-md-2">
             <div class="row q-col-gutter-sm">
               <div class="col-8">
                 <q-btn 
                   color="primary" 
                   label="Обновить" 
                   icon="refresh"
                   @click="loadFireData" 
                   :loading="loading"
                   class="full-width"
                 />
               </div>
               <div class="col-4">
                 <q-btn 
                   color="secondary" 
                   icon="visibility"
                   @click="forceShowData" 
                   :disabled="fireData.length === 0"
                   class="full-width"
                 >
                   <q-tooltip>Показать данные</q-tooltip>
                 </q-btn>
               </div>
             </div>
           </div>
         </div>

          <!-- Карта -->
          <div class="map-container">
            <div id="historical-fire-map" style="height: 500px; border-radius: 8px; overflow: hidden;"></div>
            
            <!-- Индикатор загрузки -->
            <div v-if="loading" class="loading-overlay">
              <q-spinner-dots size="50px" color="primary" />
              <div class="text-subtitle1 q-mt-md">Загрузка данных...</div>
            </div>
            
            <!-- Статус данных -->
            <div v-if="!loading && fireData.length > 0" class="data-status">
              <q-badge color="positive" :label="`${fireData.length} пожаров загружено`" />
              <q-badge v-if="displayedPointsCount > 0" color="info" :label="`Показано: ${displayedPointsCount}`" class="q-ml-sm" />
            </div>
            
            <!-- Статус без данных -->
            <div v-if="!loading && fireData.length === 0" class="data-status">
              <q-badge color="warning" label="Нет данных" />
            </div>
          </div>

        <!-- Легенда -->
        <div class="legend q-mt-md">
          <div class="text-subtitle2 text-weight-medium q-mb-sm">Легенда:</div>
          <div class="row q-col-gutter-sm">
            <div class="col-auto" v-for="severity in severityColors" :key="severity.value">
              <div class="legend-item">
                <div class="legend-color" :style="{ backgroundColor: severity.color }"></div>
                <span class="legend-label">{{ severity.label }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Статистика -->
        <div class="statistics q-mt-lg">
          <div class="row q-col-gutter-md">
            <div class="col-12 col-md-3" v-for="stat in statistics" :key="stat.label">
              <div class="stat-card">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.label }}</div>
              </div>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Диалог с деталями пожара -->
    <q-dialog v-model="showFireDialog" persistent>
      <q-card style="min-width: 350px">
        <q-card-section class="row items-center">
          <q-icon name="local_fire_department" color="red" size="28px" class="q-mr-md" />
          <span class="text-h6">Детали пожара</span>
        </q-card-section>

        <q-card-section v-if="selectedFire">
          <div class="fire-details">
            <div class="detail-row">
              <span class="detail-label">ID:</span>
              <span class="detail-value">{{ selectedFire.id }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Дата:</span>
              <span class="detail-value">{{ formatDate(selectedFire.dt) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Тип пожара:</span>
              <span class="detail-value">{{ selectedFire.type_name }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Серьезность:</span>
              <span class="detail-value">{{ getSeverityLabel(selectedFire.severity) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Координаты:</span>
              <span class="detail-value">{{ selectedFire.latitude.toFixed(4) }}, {{ selectedFire.longitude.toFixed(4) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Год:</span>
              <span class="detail-value">{{ selectedFire.year }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Месяц:</span>
              <span class="detail-value">{{ selectedFire.month }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">День недели:</span>
              <span class="detail-value">{{ getWeekdayName(selectedFire.weekday) }}</span>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Закрыть" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'

const $q = useQuasar()

// Состояние
const loading = ref(false)
const fireData = ref([])
const selectedYear = ref({ label: 'Все годы', value: 'all' })
const selectedSeverity = ref({ label: 'Все уровни', value: 'all' })
const selectedRegion = ref({ label: 'Все регионы', value: 'all' })
const showPolygons = ref(true)
const selectedFire = ref(null)
const showFireDialog = ref(false)
const maxPoints = ref(300)
const displayedPointsCount = ref(0)
const currentDetailLevel = ref('zones')
const isDataLoaded = ref(false)

// Опции фильтров
const yearOptions = ref([
  { label: 'Все годы', value: 'all' }
])

const severityOptions = ref([
  { label: 'Все уровни', value: 'all' },
  { label: 'Низкий', value: 'low' },
  { label: 'Средний', value: 'medium' },
  { label: 'Высокий', value: 'high' },
  { label: 'Критический', value: 'critical' }
])

const regionOptions = ref([
  { label: 'Все регионы', value: 'all' },
  { label: 'Россия', value: 'Россия' }
])

// Цвета для серьезности
const severityColors = ref([
  { value: 'low', label: 'Низкий', color: '#4CAF50' },
  { value: 'medium', label: 'Средний', color: '#FF9800' },
  { value: 'high', label: 'Высокий', color: '#F44336' },
  { value: 'critical', label: 'Критический', color: '#9C27B0' }
])

// Статистика
const statistics = computed(() => [
  { label: 'Всего пожаров', value: fireData.value.length },
  { label: 'Критические', value: fireData.value.filter(f => f.severity === 'critical').length },
  { label: 'Высокие', value: fireData.value.filter(f => f.severity === 'high').length },
  { label: 'Средние', value: fireData.value.filter(f => f.severity === 'medium').length }
])



// Карта
let map = null
let firePolygons = L.layerGroup()
let fireMarkers = L.layerGroup()
let markerCluster = null
let resizeObserver = null
let currentZoom = 0



// Получение цвета по серьезности
function getSeverityColor(severity) {
  const colorMap = {
    'low': '#22c55e',
    'medium': '#f59e0b', 
    'high': '#ef4444',
    'critical': '#8b5cf6'
  }
  return colorMap[severity] || '#22c55e'
}

function getSeverityLabel(severity) {
  const labelMap = {
    'low': 'Низкий',
    'medium': 'Средний',
    'high': 'Высокий', 
    'critical': 'Критический'
  }
  return labelMap[severity] || 'Неизвестно'
}

// Форматирование даты
function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

//

// Показать детали пожара
function showFireDetails(fire) {
  selectedFire.value = fire
  showFireDialog.value = true
}

// Создание полигона для области пожара
function createFirePolygon(fire) {
  const center = [fire.latitude, fire.longitude]
  
  // Увеличиваем размеры полигонов
  const radius = fire.severity === 'critical' ? 0.5 : 
                 fire.severity === 'high' ? 0.4 : 
                 fire.severity === 'medium' ? 0.3 : 0.2
  
  // Создаем круглый полигон
  const points = []
  const segments = 32 // Увеличиваем количество сегментов
  for (let i = 0; i < segments; i++) {
    const angle = (i / segments) * 2 * Math.PI
    const lat = center[0] + radius * Math.cos(angle)
    const lng = center[1] + radius * Math.sin(angle)
    points.push([lat, lng])
  }
  
  const color = getSeverityColor(fire.severity)
  
  return L.polygon(points, {
    color: color,
    weight: 4, // Увеличиваем толщину
    fillColor: color,
    fillOpacity: 0.6, // Увеличиваем прозрачность
    opacity: 0.8
  })
}

// Создание маркера для точки пожара
function createFireMarker(fire) {
  const center = [fire.latitude, fire.longitude]
  const color = getSeverityColor(fire.severity)
  
  // Увеличиваем размеры маркеров
  const radius = fire.severity === 'critical' ? 12 : 
                 fire.severity === 'high' ? 10 : 
                 fire.severity === 'medium' ? 8 : 6
  
  return L.circleMarker(center, {
    radius: radius,
    color: color,
    weight: 3, // Увеличиваем толщину
    fillColor: color,
    fillOpacity: 0.8, // Увеличиваем прозрачность
    opacity: 1
  })
}

// Переключение между полигонами и маркерами
async function updateMapLayers() {
  console.log('=== ОБНОВЛЕНИЕ СЛОЕВ КАРТЫ ===')
  
  if (!map) {
    console.error('Карта не инициализирована!')
    return
  }
  
  const zoom = map.getZoom()
  const detailLevel = getDetailLevel(zoom)
  
  console.log(`Зум: ${zoom}, Уровень детализации: ${detailLevel}`)
  console.log('Текущий уровень в памяти:', currentDetailLevel.value)
  console.log('Показывать полигоны:', showPolygons.value)
  
  // Проверяем, нужно ли загружать новые данные
  if (detailLevel !== currentDetailLevel.value || !isDataLoaded.value) {
    console.log('Нужно загрузить новые данные для уровня:', detailLevel)
    await loadDataForDetailLevel(detailLevel)
  }
  
  // Убираем все слои сначала
  console.log('Убираем слои с карты...')
  map.removeLayer(firePolygons)
  map.removeLayer(fireMarkers)
  if (markerCluster) {
    map.removeLayer(markerCluster)
  }
  
  if (showPolygons.value) {
    if (detailLevel === 'zones') {
      // Показываем упрощенные зоны
      console.log('Показываем упрощенные зоны...')
      
      fireData.value.forEach(zone => {
        const polygon = L.circle([zone.latitude, zone.longitude], {
          radius: 100000, // 100km радиус - увеличиваем
          color: getSeverityColor(zone.severity),
          weight: 5, // Увеличиваем толщину
          fillColor: getSeverityColor(zone.severity),
          fillOpacity: 0.4 // Увеличиваем прозрачность
        })
        
        polygon.on('click', () => {
          console.log(`Зона с ${zone.fireCount} пожарами`)
          $q.notify({
            message: `Зона: ${zone.fireCount} пожаров`,
            color: 'info'
          })
        })
        
        firePolygons.addLayer(polygon)
      })
      
      firePolygons.addTo(map)
      console.log(`Добавлено ${fireData.value.length} упрощенных зон`)
      displayedPointsCount.value = fireData.value.length
    } else {
      // Показываем все полигоны
      console.log('Показываем все полигоны...')
      
      fireData.value.forEach(fire => {
        const polygon = createFirePolygon(fire)
        polygon.on('click', () => {
          console.log('Клик по полигону:', fire)
          showFireDetails(fire)
        })
        firePolygons.addLayer(polygon)
      })
      
      firePolygons.addTo(map)
      console.log('Полигоны добавлены на карту')
      displayedPointsCount.value = fireData.value.length
    }
  } else {
    if (detailLevel === 'zones') {
      // Показываем упрощенные зоны как маркеры
      console.log('Показываем упрощенные зоны как маркеры...')
      
      fireData.value.forEach(zone => {
        const marker = L.circleMarker([zone.latitude, zone.longitude], {
          radius: 25, // Увеличиваем размер
          color: getSeverityColor(zone.severity),
          weight: 3, // Увеличиваем толщину
          fillColor: getSeverityColor(zone.severity),
          fillOpacity: 0.8 // Увеличиваем прозрачность
        })
        
        marker.bindPopup(`Зона: ${zone.fireCount} пожаров`)
        fireMarkers.addLayer(marker)
      })
      
      fireMarkers.addTo(map)
      console.log(`Добавлено ${fireData.value.length} упрощенных зон-маркеров`)
      displayedPointsCount.value = fireData.value.length
    } else if (detailLevel === 'clusters') {
      // Показываем кластеризованные маркеры
      console.log('Показываем кластеризованные маркеры...')
      
      fireData.value.forEach(fire => {
        const marker = createFireMarker(fire)
        marker.on('click', () => {
          console.log('Клик по маркеру:', fire)
          showFireDetails(fire)
        })
        markerCluster.addLayer(marker)
      })
      
      markerCluster.addTo(map)
      console.log('Кластеры маркеров добавлены на карту')
      displayedPointsCount.value = fireData.value.length
    } else {
      // Показываем ограниченное количество точек
      console.log('Показываем ограниченное количество точек...')
      
      fireData.value.forEach(fire => {
        const marker = createFireMarker(fire)
        marker.on('click', () => {
          console.log('Клик по маркеру:', fire)
          showFireDetails(fire)
        })
        fireMarkers.addLayer(marker)
      })
      
      fireMarkers.addTo(map)
      console.log(`Добавлено ${fireData.value.length} ограниченных маркеров`)
      displayedPointsCount.value = fireData.value.length
    }
  }
  
  console.log('Состояние слоев после обновления:')
  console.log('- Полигоны на карте:', map.hasLayer(firePolygons))
  console.log('- Маркеры на карте:', map.hasLayer(fireMarkers))
  console.log('- Кластеры на карте:', markerCluster ? map.hasLayer(markerCluster) : false)
  console.log('=== ОБНОВЛЕНИЕ СЛОЕВ ЗАВЕРШЕНО ===')
}

// Загрузка данных о пожарах
async function loadFireData() {
  console.log('=== ЗАГРУЗКА ДАННЫХ О ПОЖАРАХ ===')
  
  if (!map) {
    console.error('Карта не инициализирована!')
    return
  }
  
  try {
    loading.value = true
    
    // Определяем начальный уровень детализации
    const initialZoom = map.getZoom()
    const initialDetailLevel = getDetailLevel(initialZoom)
    console.log(`Начальный зум: ${initialZoom}, уровень: ${initialDetailLevel}`)
    
    // Загружаем данные для начального уровня
    await loadDataForDetailLevel(initialDetailLevel)
    
    // Обновляем слои
    await updateMapLayers()
    
    console.log('=== ЗАГРУЗКА ДАННЫХ ЗАВЕРШЕНА ===')
    
  } catch (error) {
    console.error('Ошибка загрузки данных о пожарах:', error)
    $q.notify({
      message: 'Ошибка загрузки данных о пожарах',
      color: 'negative'
    })
  } finally {
    loading.value = false
  }
}

// Функция для принудительного отображения данных
async function forceShowData() {
  console.log('Принудительно показываем данные...')
  currentZoom = map ? map.getZoom() : 0
  await updateMapLayers()
}

// Функция для загрузки данных в зависимости от уровня детализации
async function loadDataForDetailLevel(detailLevel) {
  console.log(`=== ЗАГРУЗКА ДАННЫХ ДЛЯ УРОВНЯ: ${detailLevel} ===`)
  
  if (!map) {
    console.error('Карта не инициализирована!')
    return
  }
  
  const zoom = map.getZoom()
  console.log(`Текущий зум: ${zoom}`)
  
  try {
    loading.value = true
    
    // Очищаем предыдущие данные
    fireData.value = []
    firePolygons.clearLayers()
    fireMarkers.clearLayers()
    if (markerCluster) {
      markerCluster.clearLayers()
    }
    
    if (detailLevel === 'zones') {
      // Для зон загружаем только агрегированные данные
      console.log('Загружаем агрегированные данные для зон...')
      
      const yearParam = selectedYear.value.value === 'all' ? new Date().getFullYear() : selectedYear.value.value
      const response = await fetch(`http://localhost:8000/api/v1/history/fires?year=${yearParam}&limit=1000`)
      if (response.ok) {
        const data = await response.json()
        console.log('Получены данные для зон:', data.length, 'записей')
        
        // Создаем упрощенные зоны
        const zones = createSimplifiedZones(data)
        console.log('Создано зон:', zones.length)
        
        // Сохраняем только зоны в памяти
        fireData.value = zones.map(zone => ({
          id: `zone_${zone.center[0]}_${zone.center[1]}`,
          latitude: zone.center[0],
          longitude: zone.center[1],
          severity: zone.severity,
          fireCount: zone.fires.length,
          region: zone.fires[0]?.region || 'Россия'
        }))
        
        currentDetailLevel.value = 'zones'
        console.log('Данные для зон загружены и сохранены')
      }
    } else if (detailLevel === 'clusters') {
      // Для кластеров загружаем больше данных
      console.log('Загружаем данные для кластеров...')
      
      const yearParam = selectedYear.value.value === 'all' ? new Date().getFullYear() : selectedYear.value.value
      const response = await fetch(`http://localhost:8000/api/v1/history/fires?year=${yearParam}&limit=5000`)
      if (response.ok) {
        const data = await response.json()
        console.log('Получены данные для кластеров:', data.length, 'записей')
        
        fireData.value = data
        currentDetailLevel.value = 'clusters'
        console.log('Данные для кластеров загружены')
      }
    } else if (detailLevel === 'points') {
      // Для точек загружаем данные только для видимой области
      console.log('Загружаем данные для точек в видимой области...')
      
      const bounds = map.getBounds()
      const yearParam = selectedYear.value.value === 'all' ? new Date().getFullYear() : selectedYear.value.value
      
      // Ограничиваем количество запрашиваемых данных
      const response = await fetch(`http://localhost:8000/api/v1/history/fires?year=${yearParam}&limit=500`)
      if (response.ok) {
        const allData = await response.json()
        console.log('Получены все данные:', allData.length, 'записей')
        
        // Фильтруем по видимой области
        const visibleData = allData.filter(fire => {
          if (!fire.latitude || !fire.longitude) return false
          return bounds.contains([fire.latitude, fire.longitude])
        })
        
        // Ограничиваем количество до 200 точек
        const limitedData = getLimitedPoints(visibleData, 200)
        console.log('Отфильтровано для видимой области:', limitedData.length, 'записей')
        
        fireData.value = limitedData
        currentDetailLevel.value = 'points'
        console.log('Данные для точек загружены')
      }
    }
    
    isDataLoaded.value = true
    console.log(`=== ЗАГРУЗКА ДАННЫХ ЗАВЕРШЕНА: ${detailLevel} ===`)
    
  } catch (error) {
    console.error('Ошибка загрузки данных:', error)
    $q.notify({
      message: 'Ошибка загрузки данных',
      color: 'negative'
    })
  } finally {
    loading.value = false
  }
}

// Функция для получения названия дня недели
function getWeekdayName(dayIndex) {
  const days = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
  return days[dayIndex] || 'Неизвестный день';
}

//

// Функция для определения уровня детализации
function getDetailLevel(zoom) {
  if (zoom < 6) return 'zones'      // Показываем только зоны
  if (zoom < 8) return 'clusters'   // Показываем кластеры
  return 'points'                    // Показываем ограниченное количество точек
}

// Функция для получения ограниченного количества точек
function getLimitedPoints(fireData, maxPoints = 500) {
  console.log(`Ограничиваем количество точек до ${maxPoints}`)
  
  // Если точек меньше лимита, возвращаем все
  if (fireData.length <= maxPoints) {
    return fireData
  }
  
  // Иначе выбираем случайные точки
  const shuffled = [...fireData].sort(() => 0.5 - Math.random())
  return shuffled.slice(0, maxPoints)
}

//

// Функция для создания упрощенных зон
function createSimplifiedZones(fireData) {
  console.log('Создаем упрощенные зоны...')
  const zones = new Map()
  
  fireData.forEach(fire => {
    if (!fire.latitude || !fire.longitude) return
    
    // Группируем по регионам или создаем зоны по сетке
    const zoneKey = fire.region || `${Math.floor(fire.longitude * 10) / 10},${Math.floor(fire.latitude * 10) / 10}`
    
    if (!zones.has(zoneKey)) {
      zones.set(zoneKey, {
        center: [fire.latitude, fire.longitude],
        fires: [],
        severity: 'medium'
      })
    }
    
    const zone = zones.get(zoneKey)
    zone.fires.push(fire)
    
    // Определяем максимальную серьезность в зоне
    if (fire.severity === 'critical' || zone.severity === 'critical') {
      zone.severity = 'critical'
    } else if (fire.severity === 'high' || zone.severity === 'high') {
      zone.severity = 'high'
    }
  })
  
  return Array.from(zones.values())
}

// Функция для загрузки доступных годов
async function loadAvailableYears() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/history/fires?limit=1000')
    if (response.ok) {
      const data = await response.json()
      const years = [...new Set(data.map(fire => fire.year))].sort((a, b) => b - a)
      
      yearOptions.value = [
        { label: 'Все годы', value: 'all' },
        ...years.map(year => ({ label: year.toString(), value: year }))
      ]
      
      console.log('Загружены доступные годы:', yearOptions.value)
    }
  } catch (error) {
    console.error('Ошибка загрузки годов:', error)
  }
}

// Инициализация
onMounted(async () => {
  try {
    console.log('Initializing historical fire map')
    
    const mapContainer = document.getElementById('historical-fire-map')
    if (!mapContainer) {
      console.error('Map container not found!')
      return
    }
    
    console.log('Map container found:', mapContainer)
    
    map = L.map('historical-fire-map', {
      zoomControl: true,
      attributionControl: false
    }).setView([61.5240, 105.3188], 3)
    
    console.log('Map created:', map)
    
    const baseLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
      attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
      maxZoom: 18,
      minZoom: 3
    }).addTo(map)
    
    console.log('Base layer added')
    
    const fallbackLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      subdomains: 'abc',
      maxZoom: 18,
      minZoom: 3
    })
    
    baseLayer.on('tileerror', function() {
      console.log('Основной слой недоступен, переключаемся на альтернативный')
      map.removeLayer(baseLayer)
      fallbackLayer.addTo(map)
    })
    
    // Создаем кластер для маркеров
    markerCluster = L.markerClusterGroup({
      chunkedLoading: true,
      chunkInterval: 200,
      chunkDelay: 50,
      maxClusterRadius: 50,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: true,
      zoomToBoundsOnClick: true,
      disableClusteringAtZoom: 10,
      removeOutsideVisibleBounds: true,
      animate: true,
      animateAddingMarkers: true
    })
    
    console.log('Marker cluster created')
    
    // Добавляем ResizeObserver
    const mapElement = document.getElementById('historical-fire-map')
    if (mapElement) {
      resizeObserver = new ResizeObserver(() => {
        if (map) {
          map.invalidateSize()
          console.log('Карта перерисована после изменения размера')
        }
      })
      resizeObserver.observe(mapElement)
    }
    
    // Добавляем слушатель зума
    map.on('zoomend', async () => {
      const newZoom = map.getZoom()
      const newDetailLevel = getDetailLevel(newZoom)
      
      if (newDetailLevel !== currentDetailLevel.value) {
        console.log(`Зум изменился: ${currentZoom} -> ${newZoom}, обновляем детализацию`)
        currentZoom = newZoom
        await updateMapLayers()
      }
    })
    
    // Добавляем слушатель перемещения карты
    map.on('moveend', async () => {
      const zoom = map.getZoom()
      if (zoom >= 8 && currentDetailLevel.value === 'points') {
        console.log('Карта перемещена, обновляем данные для точек')
        await loadDataForDetailLevel('points')
        await updateMapLayers()
      }
    })
    
    console.log('Map initialized, loading fire data')
    
    // Инициализируем текущий зум
    currentZoom = map.getZoom()
    console.log(`Начальный зум: ${currentZoom}`)
    
    // Создаем кластер для маркеров
    markerCluster = L.markerClusterGroup({
      chunkedLoading: true,
      chunkInterval: 200,
      chunkDelay: 50,
      maxClusterRadius: 50,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: true,
      zoomToBoundsOnClick: true,
      disableClusteringAtZoom: 10,
      removeOutsideVisibleBounds: true,
      animate: true,
      animateAddingMarkers: true
    })
    
    // Загружаем доступные годы
    await loadAvailableYears()
    
    await loadFireData()
    
  } catch (error) {
    console.error('Error initializing map:', error)
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style lang="scss" scoped>
.historical-fire-map {
  .map-card {
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
      background: linear-gradient(135deg, rgba(244, 67, 54, 0.1), rgba(156, 39, 176, 0.1));
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding: 1.5rem;
    }

    .card-content {
      padding: 1.5rem;
    }
  }

  .filter-input {
    border-radius: 12px;
    
    .q-field__control {
      border-radius: 12px;
    }
  }

  .map-container {
    position: relative;
    height: 500px;
    border-radius: 12px;
    overflow: hidden;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  }

  .map-wrapper {
    height: 100%;
    width: 100%;
    position: relative;
  }

  .map-background {
    height: 100%;
    width: 100%;
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    position: relative;
    border-radius: 12px;
    border: 2px solid rgba(244, 67, 54, 0.1);
    overflow: hidden;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M10,20 Q30,10 50,20 Q70,30 90,20 L90,80 Q70,90 50,80 Q30,70 10,80 Z" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="0.5"/></svg>') repeat;
      opacity: 0.3;
      pointer-events: none;
    }
  }

     .fire-point {
     position: absolute;
     transform: translate(-50%, -50%);
     cursor: pointer;
     transition: all 0.2s ease;
     z-index: 10;

     &:hover {
       transform: translate(-50%, -50%) scale(1.5);
       z-index: 20;
     }

     .fire-marker {
       width: 12px;
       height: 12px;
       border-radius: 50%;
       border: 2px solid white;
       box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
       transition: all 0.2s ease;
       display: flex;
       align-items: center;
       justify-content: center;
       position: relative;
     }
   }

   .fire-cluster {
     .fire-marker {
       border: 3px solid white;
       box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
       
       .cluster-count {
         color: white;
         font-size: 0.7rem;
         font-weight: bold;
         text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
       }
     }
   }

  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 100;
    border-radius: 12px;
  }

  .no-data-hint {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    color: #666;
  }

  .points-counter {
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 50;
  }

  .legend {
    .legend-item {
      display: flex;
      align-items: center;
      margin-right: 16px;
      margin-bottom: 8px;

      .legend-color {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        margin-right: 8px;
        border: 2px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }

      .legend-label {
        font-size: 0.875rem;
        color: #666;
      }
    }
  }

  .statistics {
    .stat-card {
      text-align: center;
      padding: 16px;
      background: rgba(244, 67, 54, 0.05);
      border-radius: 12px;
      border: 1px solid rgba(244, 67, 54, 0.1);
      transition: all 0.2s ease;

      &:hover {
        background: rgba(244, 67, 54, 0.1);
        transform: translateY(-2px);
      }

      .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f44336;
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: 0.875rem;
        color: #666;
      }
    }
  }

  .fire-details {
    .detail-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
        margin-bottom: 0;
      }

      .detail-label {
        font-weight: 600;
        color: #666;
      }

      .detail-value {
        color: #333;
        text-align: right;
      }
    }
  }
}

:deep(.fire-marker) {
  animation: pulse 2s infinite;
  box-shadow: 0 0 10px rgba(244, 67, 54, 0.8);
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

:deep(.leaflet-interactive) {
  transition: all 0.3s ease;
}

:deep(.leaflet-interactive:hover) {
  transform: scale(1.2);
  z-index: 1000 !important;
}

// Responsive adjustments
@media (max-width: 768px) {
  .historical-fire-map {
    .map-container {
      height: 350px;
    }

    .legend {
      .legend-item {
        margin-right: 8px;
        
        .legend-label {
          font-size: 0.75rem;
        }
      }
    }

    .statistics {
      .stat-card {
        padding: 12px;
        
        .stat-value {
          font-size: 1.25rem;
        }
        
        .stat-label {
          font-size: 0.75rem;
        }
      }
    }
  }
}
</style>
