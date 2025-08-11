<template>
  <div class="map-container">
    <div id="dashboard-map-container" style="height: 400px; border-radius: 8px; overflow: hidden;"></div>
  </div>

  <!-- Модальное окно для информации о пожаре -->
  <q-dialog v-model="showFireInfo" @keydown.esc="showFireInfo = false">
    <q-card class="fire-info-modal" style="background-color: #1e293b; color: white;">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Информация о пожаре</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup color="white" />
      </q-card-section>

      <q-card-section v-if="selectedFire" class="q-pt-md">
        <div class="bg-orange-8 text-white q-pa-md q-mb-md rounded-borders text-center text-weight-bold">
          {{ getRiskLabel(selectedFire.risk) }}
        </div>

        <div class="row q-col-gutter-md">
          <div class="col-6">
            <div class="text-grey-4">Координаты</div>
            <div class="text-white text-weight-medium">{{ selectedFire.lat.toFixed(3) }}, {{
              selectedFire.lng.toFixed(3) }}</div>
          </div>
          <div class="col-6">
            <div class="text-grey-4">Дата прогноза</div>
            <div class="text-white text-weight-medium">{{ formatOnlyDate(selectedFire?.createdAt) }}</div>
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
            <div class="text-grey-4">Вероятность возникновения</div>
            <div class="text-white text-weight-medium">{{ formatPercent(selectedFire?.probability) }}%</div>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="center" class="q-pa-md">
        <q-btn flat label="ПОДРОБНЕЕ" color="blue-5" class="q-px-md" icon="visibility" v-close-popup />
        <q-btn flat label="МАРШРУТ" color="teal-5" class="q-px-md" icon="directions" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <!-- Модальное окно для наблюдения Рослесхоза -->
  <q-dialog v-model="showRosleshozInfo" @keydown.esc="showRosleshozInfo = false">
    <q-card class="fire-info-modal" style="background-color: #0f172a; color: white; min-width: 320px;">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Активный пожар (регион)</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup color="white" />
      </q-card-section>

      <q-card-section v-if="selectedObservation" class="q-pt-md">
        <div class="bg-red-7 text-white q-pa-md q-mb-md rounded-borders text-center text-weight-bold">
          Наблюдение Рослесхоза
        </div>

        <div class="q-mb-sm">
          <div class="text-grey-4">Регион</div>
          <div class="text-white text-weight-medium">{{ selectedObservation.name }}</div>
        </div>

        <div class="q-mb-sm">
          <div class="text-grey-4">Дата бюллетеня</div>
          <div class="text-white text-weight-medium">{{ selectedObservation.date || '—' }}</div>
        </div>

        <div class="text-caption text-grey-5">Источник: Рослесхоз</div>
      </q-card-section>

      <q-card-actions align="center" class="q-pa-md">
        <q-btn flat label="Закрыть" color="red-4" class="q-px-md" icon="close" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster' 
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'

let map = null
let resizeObserver = null
let markerClusterGroup = null
let refreshTimer = null
let rosleshozLayer = null
const showFireInfo = ref(false)
const showRosleshozInfo = ref(false)
const selectedFire = ref({
  id: 3,
  name: '',
  risk: 'high',
  temperature: 30,
  humidity: 18,
  createdAt: undefined
})

const selectedObservation = ref({
  name: '',
  date: ''
})

function getRiskLabel(risk) {
  const labels = {
    'low': 'Низкий',
    'medium': 'Средний',
    'high': 'Высокий',
    'critical': 'Критический'
  }
  return labels[risk] || 'Неизвестно'
}

function formatOnlyDate(value) {
  if (!value) return ''
  const d = new Date(value)
  if (isNaN(d.getTime())) return ''
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  return `${dd}.${mm}.${yyyy}`
}

function formatPercent(v) {
  const n = Number(v)
  if (!isFinite(n)) return '0.0'
  return (Math.round(n * 10) / 10).toFixed(1)
}

function openFireInfo(fire) {
  selectedFire.value = fire
  showFireInfo.value = true
}

function openRosleshozInfo(obs) {
  selectedObservation.value = obs
  showRosleshozInfo.value = true
}

onMounted(async () => {
  try {
    console.log('Initializing dashboard map')

    const mapContainer = document.getElementById('dashboard-map-container')
    if (!mapContainer) {
      console.error('Map container not found!')
      return
    }

    console.log('Map container found, initializing Leaflet map')

    map = L.map('dashboard-map-container', {
      zoomControl: true,
      attributionControl: false
    }).setView([61.5240, 105.3188], 3)

    const baseLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
      attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
      maxZoom: 18,
      minZoom: 3
    }).addTo(map)

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

    console.log('Map initialized, adding markers')

    async function loadPredictionMarkers() {
      const fireMarkers = await fetch('http://localhost:8000/api/v1/predictions/history?limit=500')
        .then(r => r.ok ? r.json() : [])
        .then(list => list.map(p => ({
          id: p.id,
          lat: p.latitude,
          lng: p.longitude,
          risk: p.risk_level,
          name: `Предсказание #${p.id}`,
          temperature: undefined,
          humidity: Math.round(p.confidence),
          createdAt: p.created_at,
          probability: p.risk_percentage
        })))
        .catch(() => [])

      // Очистить прошлые маркеры
      if (markerClusterGroup) {
        markerClusterGroup.clearLayers()
      }

      fireMarkers.forEach(marker => {
        let color = 'green'
        if (marker.risk === 'medium') color = 'orange'
        if (marker.risk === 'high') color = 'red'
        if (marker.risk === 'critical') color = 'purple'

        const circleMarker = L.circleMarker([marker.lat, marker.lng], {
          radius: marker.risk === 'critical' ? 12 : marker.risk === 'high' ? 10 : 8,
          fillColor: color,
          color: 'white',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.9,
          interactive: true,
          bubblingMouseEvents: false,
          className: marker.risk === 'critical' || marker.risk === 'high' ? 'fire-marker' : ''
        })

        circleMarker.on('click', () => {
          openFireInfo({
            id: marker.id,
            risk: marker.risk,
            lat: marker.lat,
            lng: marker.lng,
            humidity: marker.humidity,
            temperature: marker.temperature,
            createdAt: marker.createdAt,
            probability: marker.probability
          })
        })

        markerClusterGroup.addLayer(circleMarker)
      })
    }

    // Создаем кластерную группу
    markerClusterGroup = L.markerClusterGroup({
      chunkedLoading: true,
      maxClusterRadius: 50,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      disableClusteringAtZoom: 12,
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

    // Первичная загрузка маркеров
    await loadPredictionMarkers()

    map.addLayer(markerClusterGroup)

    console.log('Markers added, updating map size')

    setTimeout(() => {
      if (map) {
        map.invalidateSize()
        console.log('Map size updated')
      }
    }, 1000)

    setTimeout(() => {
      if (map) {
        map.invalidateSize()
        console.log('Map size updated again')
      }
    }, 2000)

    resizeObserver = new ResizeObserver(() => {
      if (map) {
        setTimeout(() => {
          map.invalidateSize()
          console.log('Map resized and invalidated')
        }, 100)
      }
    })

    resizeObserver.observe(mapContainer)

    // Слой наблюдений Рослесхоза
    rosleshozLayer = L.layerGroup().addTo(map)
    async function loadRosleshozObservations() {
      try {
        const data = await fetch('http://localhost:8000/api/v1/data/rosleshoz/operative').then(r => r.json())
        rosleshozLayer.clearLayers()
        const pts = data.region_points || []
        console.log('[Rosleshoz] points:', pts.length, 'date:', data.bulletin_date)
        pts.forEach(p => {
          const marker = L.circleMarker([p.latitude, p.longitude], {
            radius: 10,
            color: 'white',
            weight: 2,
            fillColor: '#e53935',
            fillOpacity: 0.95
          })
          marker.bindTooltip(`Активный пожар (регион): ${p.name}`, { sticky: true })
          marker.on('click', () => {
            // показываем дату из fetched_at, только дата без времени
            let date = ''
            if (data.fetched_at) {
              const d = new Date(data.fetched_at)
              if (!isNaN(d.getTime())) {
                const dd = String(d.getDate()).padStart(2, '0')
                const mm = String(d.getMonth() + 1).padStart(2, '0')
                const yyyy = d.getFullYear()
                date = `${dd}.${mm}.${yyyy}`
              }
            }
            openRosleshozInfo({ name: p.name, date })
          })
          rosleshozLayer.addLayer(marker)
        })
      } catch { /* ignore */ }
    }
    await loadRosleshozObservations()
    // обновлять каждые 30 мин
    setInterval(loadRosleshozObservations, 30 * 60 * 1000)

    // Периодическое обновление (новые и старые предикты)
    refreshTimer = setInterval(loadPredictionMarkers, 30000)
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
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})
</script>

<style lang="scss" scoped>
.map-container {
  width: 100%;
  height: 400px;
}

f .fire-info-modal {
  min-width: 300px;
  border-radius: 12px;
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