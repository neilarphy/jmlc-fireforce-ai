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
            <div class="text-grey-4">Дата обнаружения</div>
            <div class="text-white text-weight-medium">22.07.2025</div>
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
            <div class="text-grey-4">Скорость ветра</div>
            <div class="text-white text-weight-medium">19 м/с</div>
          </div>
          <div class="col-6">
            <div class="text-grey-4">Статус</div>
            <div class="text-white text-weight-medium">Активный</div>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="center" class="q-pa-md">
        <q-btn flat label="ПОДРОБНЕЕ" color="blue-5" class="q-px-md" icon="visibility" v-close-popup />
        <q-btn flat label="МАРШРУТ" color="teal-5" class="q-px-md" icon="directions" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

let map = null
let resizeObserver = null
const showFireInfo = ref(false)
const selectedFire = ref({
  id: 3,
  name: '',
  risk: 'high',
  temperature: 30,
  humidity: 18
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

function openFireInfo(fire) {
  selectedFire.value = fire
  showFireInfo.value = true
}

onMounted(() => {
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

    // Альтернативный слой на случай проблем с основным
    const fallbackLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      subdomains: 'abc',
      maxZoom: 18,
      minZoom: 3
    })

    // Проверяем загрузку основного слоя
    baseLayer.on('tileerror', function() {
      console.log('Основной слой недоступен, переключаемся на альтернативный')
      map.removeLayer(baseLayer)
      fallbackLayer.addTo(map)
    })

    console.log('Map initialized, adding markers')

    const fireMarkers = [
      { id: 1, lat: 55.7558, lng: 37.6173, risk: 'high', name: 'Москва', temperature: 28, humidity: 22 },
      { id: 2, lat: 59.9311, lng: 30.3609, risk: 'medium', name: 'Санкт-Петербург', temperature: 25, humidity: 30 },
      { id: 3, lat: 56.8431, lng: 60.6454, risk: 'high', name: 'Екатеринбург', temperature: 30, humidity: 18 },
      { id: 4, lat: 56.0184, lng: 92.8672, risk: 'critical', name: 'Красноярск', temperature: 32, humidity: 15 },
      { id: 5, lat: 43.1056, lng: 131.8735, risk: 'low', name: 'Владивосток', temperature: 24, humidity: 40 }
    ]

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
      }).addTo(map)

      circleMarker.on('click', () => {
        openFireInfo(marker)
      })
    })

    console.log('Markers added, updating map size')

    setTimeout(() => {
      if (map) {
        map.invalidateSize()
        console.log('Map size updated')
      }
    }, 1000)

    // Дополнительная проверка через 2 секунды
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
</style>