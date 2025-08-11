<template>
  <div class="map-selector">
    <!-- Кнопка для открытия карты -->
    <q-btn
      :label="buttonLabel"
      :icon="buttonIcon"
      color="primary"
      outline
      class="map-button q-mb-md"
      @click="showMap = true"
    />
    
         <!-- Диалог с картой -->
     <q-dialog v-model="showMap" @keydown.esc="closeMap" @click="handleBackdropClick">
      <q-card class="map-dialog">
        <q-card-section class="card-header">
          <div class="row items-center">
            <q-icon name="map" size="28px" color="primary" class="q-mr-md" />
            <div class="text-h6 text-weight-bold">Выберите координаты на карте</div>
            <q-space />
            <q-btn icon="close" flat round dense @click="closeMap" />
          </div>
        </q-card-section>
        
                          <q-card-section class="map-container">
           <!-- Выбор города -->
           <div class="search-container q-mb-md">
             <div class="row q-col-gutter-md">
               <div class="col-12">
                 <CitySelector :on-select="handleCitySelect" />
               </div>
             </div>
             <!-- Кнопка под полем ввода -->
             <div class="button-container q-mt-md">
               <q-btn 
                 unelevated 
                 label="ПОДТВЕРДИТЬ ВЫБОР" 
                 color="primary" 
                 size="lg"
                 @click="selectCoordinates"
                 :disable="!coordinatesSelected"
                 class="confirm-button"
               />
             </div>
           </div>
           
                                <!-- Карта -->
            <div ref="mapContainer" class="map-wrapper">
              <div id="map" class="map"></div>
              <div class="map-overlay">
                <div class="coordinates-display">
                  <div class="coord-item">
                    <span class="coord-label">Широта:</span>
                    <span class="coord-value">{{ selectedLatitude.toFixed(4) }}</span>
                  </div>
                  <div class="coord-item">
                    <span class="coord-label">Долгота:</span>
                    <span class="coord-value">{{ selectedLongitude.toFixed(4) }}</span>
                  </div>
                </div>
              </div>
              <div class="map-hint">
                <q-icon name="info" size="16px" color="white" />
                <span>Кликните на карту для выбора точки</span>
              </div>
            </div>
        </q-card-section>
        
        
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { useQuasar } from 'quasar';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import CitySelector from './CitySelector.vue';

const $q = useQuasar();

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ latitude: 55.7558, longitude: 37.6173 })
  },
  buttonLabel: {
    type: String,
    default: 'Выбрать на карте'
  },
  buttonIcon: {
    type: String,
    default: 'map'
  }
});

// Emits
const emit = defineEmits(['update:modelValue']);

// Reactive data
const showMap = ref(false);
const mapContainer = ref(null);
const selectedLatitude = ref(props.modelValue.latitude);
const selectedLongitude = ref(props.modelValue.longitude);
const coordinatesSelected = ref(true); // Всегда true, чтобы кнопка была активна
let map = null;
let marker = null;

// Methods
async function initMap() {
  if (!mapContainer.value) return;
  
  try {
    // Уничтожаем предыдущую карту если есть
    if (map) {
      map.remove();
    }
    
    // Инициализируем карту
    map = L.map('map', {
      zoomControl: false, // Отключаем стандартные элементы управления
      attributionControl: false, // Отключаем атрибуцию
      scrollWheelZoom: true,
      dragging: true,
      touchZoom: true,
      doubleClickZoom: true,
      boxZoom: false,
      keyboard: false,
      tap: true
    }).setView([selectedLatitude.value, selectedLongitude.value], 8);
    
    // Добавляем слой OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
         // Создаем простой и надежный маркер
     const customIcon = L.divIcon({
       html: '<div class="simple-marker">📍</div>',
       className: 'simple-marker-container',
       iconSize: [60, 60],
       iconAnchor: [30, 60] // Якорная точка внизу маркера
     });
     
     // Добавляем маркер
     marker = L.marker([selectedLatitude.value, selectedLongitude.value], { 
       icon: customIcon,
       draggable: false,
       clickTolerance: 0
     }).addTo(map);
    
         console.log('Marker added at:', selectedLatitude.value, selectedLongitude.value);
     console.log('Marker element:', marker.getElement());
     console.log('Marker icon:', marker.getIcon());
     console.log('Map bounds:', map.getBounds());
    
         // Обработчик клика по карте
     map.on('click', function(e) {
       const lat = e.latlng.lat;
       const lng = e.latlng.lng;
       
       console.log('Map clicked at:', lat, lng);
       
       selectedLatitude.value = lat;
       selectedLongitude.value = lng;
       coordinatesSelected.value = true;
       
       // Обновляем маркер
       if (marker) {
         marker.setLatLng([lat, lng]);
         console.log('Marker moved to:', lat, lng);
       } else {
                   const newIcon = L.divIcon({
            html: '<div class="simple-marker">📍</div>',
            className: 'simple-marker-container',
            iconSize: [60, 60],
            iconAnchor: [30, 60] // Якорная точка внизу маркера
          });
         marker = L.marker([lat, lng], { icon: newIcon }).addTo(map);
         console.log('New marker created at:', lat, lng);
       }
       
       
     });
    
    // Добавляем кастомные элементы управления только для зума
    const zoomControl = L.control.zoom({
      position: 'topright'
    });
    zoomControl.addTo(map);
    
    console.log('Map initialized successfully');
  } catch (error) {
    console.error('Error initializing map:', error);
    $q.notify({
      type: 'negative',
      message: 'Ошибка загрузки карты'
    });
  }
}

function closeMap() {
  console.log('Closing map dialog');
  showMap.value = false;
  // Уничтожаем карту при закрытии
  if (map) {
    map.remove();
    map = null;
    marker = null;
  }
}

function handleBackdropClick(event) {
  // Закрываем только если клик был по фону (не по карточке)
  if (event.target.classList.contains('q-dialog__backdrop')) {
    closeMap();
  }
}

function selectCoordinates() {
  console.log('Selecting coordinates:', selectedLatitude.value, selectedLongitude.value);
  const newValue = {
    latitude: selectedLatitude.value,
    longitude: selectedLongitude.value
  };
  console.log('Emitting new value:', newValue);
  
  
  
  emit('update:modelValue', newValue);
  emit('coordinates-selected', newValue);
  closeMap();
}





function handleCitySelect(city) {
  selectedLatitude.value = city.latitude;
  selectedLongitude.value = city.longitude;
  coordinatesSelected.value = true;
  
  // Обновляем карту
  if (map) {
    map.setView([city.latitude, city.longitude], 10);
    if (marker) {
      marker.setLatLng([city.latitude, city.longitude]);
         } else {
                        // Создаем простой маркер
         const customIcon = L.divIcon({
           html: '<div class="simple-marker">📍</div>',
           className: 'simple-marker-container',
           iconSize: [60, 60],
           iconAnchor: [30, 60] // Якорная точка внизу маркера
         });
       marker = L.marker([city.latitude, city.longitude], { 
         icon: customIcon,
         draggable: false,
         clickTolerance: 0
       }).addTo(map);
     }
  }
  
  
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  console.log('Model value changed:', newValue);
  selectedLatitude.value = newValue.latitude;
  selectedLongitude.value = newValue.longitude;
}, { deep: true });

// Lifecycle
watch(showMap, async (newValue) => {
  if (newValue) {
    // Ждем следующего тика для обновления DOM
    await nextTick();
    // Инициализируем карту когда диалог открывается
    setTimeout(() => {
      initMap();
    }, 100);
  }
});
</script>

<style scoped>
.map-selector {
  width: 100%;
}

.map-button {
  width: 100%;
}

.map-dialog {
  width: 80vw;
  max-width: 1000px;
  height: 75vh;
}

.map-container {
  padding: 12px;
  height: calc(75vh - 200px);
}

.search-container {
  background: var(--q-card-bg);
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 12px;
  z-index: 1000;
  position: relative;
  border: 1px solid var(--q-separator-color);
}

.button-container {
  text-align: center;
}

.confirm-button {
  width: 100%;
  font-weight: bold;
}

.map-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.map {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  z-index: 1;
}

.map-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.coordinates-display {
  font-family: monospace;
  font-size: 12px;
}

.coord-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.coord-label {
  color: rgba(255, 255, 255, 0.8);
  margin-right: 10px;
}

.coord-value {
  font-weight: bold;
  color: white;
}

.map-hint {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 1000;
  backdrop-filter: blur(10px);
}





.card-header {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}



/* Скрываем стандартные иконки Leaflet */
.leaflet-default-icon-path,
.leaflet-default-shadow-path {
  display: none;
}

/* Скрываем стандартную атрибуцию */
.leaflet-control-attribution {
  display: none !important;
}

/* Скрываем вертикальный слайдер и другие ненужные элементы */
.leaflet-control-zoom {
  border: none !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}

.leaflet-control-zoom a {
  background: rgba(255, 255, 255, 0.9) !important;
  color: #333 !important;
  border: none !important;
  border-radius: 4px !important;
  margin: 2px !important;
}

.leaflet-control-zoom a:hover {
  background: rgba(255, 255, 255, 1) !important;
}

/* Скрываем все остальные стандартные элементы */
.leaflet-control-layers,
.leaflet-control-scale {
  display: none !important;
}

/* Улучшаем стили для полей поиска */
.search-container .q-input {
  background: var(--q-input-bg);
  border-radius: 4px;
}

.search-container .q-field__control {
  background: var(--q-input-bg) !important;
  border-color: var(--q-input-border-color) !important;
}

.search-container .q-field__native {
  color: var(--q-input-text-color) !important;
}

.search-container .q-field__label {
  color: var(--q-input-label-color) !important;
}

.search-container .q-field--focused .q-field__control {
  border-color: var(--q-primary) !important;
}

/* Простой и надежный маркер */
.simple-marker-container {
  background: transparent !important;
  border: none !important;
  z-index: 99999 !important;
}

.simple-marker {
  font-size: 60px;
  color: #ff0000;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9);
  filter: drop-shadow(0 6px 12px rgba(255, 0, 0, 0.7));
  z-index: 99999;
}

/* Принудительно показываем маркер */
.leaflet-marker-icon {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.leaflet-marker-icon,
.leaflet-marker-shadow {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}
</style> 