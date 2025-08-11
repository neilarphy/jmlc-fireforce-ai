<template>
  <div class="city-selector">
    <q-select
      v-model="selectedCity"
      :options="filteredCities"
      option-label="name"
      option-value="name"
      label="Выберите город"
      outlined
      dense
      use-input
      input-debounce="300"
      @filter="filterCities"
      @update:model-value="onCitySelect"
    >
      <template v-slot:option="scope">
        <q-item v-bind="scope.itemProps">
          <q-item-section>
            <q-item-label>{{ scope.opt.name }}</q-item-label>
            <q-item-label caption>{{ scope.opt.coordinates }}</q-item-label>
          </q-item-section>
        </q-item>
      </template>
    </q-select>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// Props
const props = defineProps({
  onSelect: {
    type: Function,
    required: true
  }
});

// Reactive data
const selectedCity = ref(null);

// Список городов РФ
const cities = ref([
  { name: 'Москва', lat: 55.7558, lng: 37.6173, coordinates: '55.7558, 37.6173' },
  { name: 'Санкт-Петербург', lat: 59.9311, lng: 30.3609, coordinates: '59.9311, 30.3609' },
  { name: 'Новосибирск', lat: 55.0084, lng: 82.9357, coordinates: '55.0084, 82.9357' },
  { name: 'Екатеринбург', lat: 56.8519, lng: 60.6122, coordinates: '56.8519, 60.6122' },
  { name: 'Казань', lat: 55.7887, lng: 49.1221, coordinates: '55.7887, 49.1221' },
  { name: 'Нижний Новгород', lat: 56.2965, lng: 43.9361, coordinates: '56.2965, 43.9361' },
  { name: 'Челябинск', lat: 55.1544, lng: 61.4297, coordinates: '55.1544, 61.4297' },
  { name: 'Самара', lat: 53.2001, lng: 50.1500, coordinates: '53.2001, 50.1500' },
  { name: 'Уфа', lat: 54.7388, lng: 55.9721, coordinates: '54.7388, 55.9721' },
  { name: 'Ростов-на-Дону', lat: 47.2357, lng: 39.7015, coordinates: '47.2357, 39.7015' },
  { name: 'Краснодар', lat: 45.0448, lng: 38.9760, coordinates: '45.0448, 38.9760' },
  { name: 'Воронеж', lat: 51.6720, lng: 39.1843, coordinates: '51.6720, 39.1843' },
  { name: 'Пермь', lat: 58.0105, lng: 56.2502, coordinates: '58.0105, 56.2502' },
  { name: 'Волгоград', lat: 48.7080, lng: 44.5133, coordinates: '48.7080, 44.5133' },
  { name: 'Красноярск', lat: 56.0184, lng: 92.8672, coordinates: '56.0184, 92.8672' },
  { name: 'Саратов', lat: 51.5924, lng: 46.0347, coordinates: '51.5924, 46.0347' },
  { name: 'Тюмень', lat: 57.1526, lng: 65.5272, coordinates: '57.1526, 65.5272' },
  { name: 'Тольятти', lat: 53.5078, lng: 49.4204, coordinates: '53.5078, 49.4204' },
  { name: 'Ижевск', lat: 56.8519, lng: 53.2324, coordinates: '56.8519, 53.2324' },
  { name: 'Барнаул', lat: 53.3548, lng: 83.7698, coordinates: '53.3548, 83.7698' },
  { name: 'Ульяновск', lat: 54.3176, lng: 48.3706, coordinates: '54.3176, 48.3706' },
  { name: 'Иркутск', lat: 52.2876, lng: 104.3050, coordinates: '52.2876, 104.3050' },
  { name: 'Хабаровск', lat: 48.4802, lng: 135.0719, coordinates: '48.4802, 135.0719' },
  { name: 'Ярославль', lat: 57.6261, lng: 39.8875, coordinates: '57.6261, 39.8875' },
  { name: 'Владивосток', lat: 43.1198, lng: 131.8869, coordinates: '43.1198, 131.8869' },
  { name: 'Махачкала', lat: 42.9849, lng: 47.5047, coordinates: '42.9849, 47.5047' },
  { name: 'Томск', lat: 56.4977, lng: 84.9744, coordinates: '56.4977, 84.9744' },
  { name: 'Оренбург', lat: 51.7727, lng: 55.0988, coordinates: '51.7727, 55.0988' },
  { name: 'Кемерово', lat: 55.3909, lng: 86.0468, coordinates: '55.3909, 86.0468' },
  { name: 'Новокузнецк', lat: 53.7945, lng: 87.1668, coordinates: '53.7945, 87.1668' },
  { name: 'Рязань', lat: 54.6269, lng: 39.6916, coordinates: '54.6269, 39.6916' },
  { name: 'Астрахань', lat: 46.3586, lng: 48.0649, coordinates: '46.3586, 48.0649' },
  { name: 'Набережные Челны', lat: 55.7436, lng: 52.3958, coordinates: '55.7436, 52.3958' },
  { name: 'Пенза', lat: 53.2007, lng: 45.0046, coordinates: '53.2007, 45.0046' },
  { name: 'Липецк', lat: 52.6031, lng: 39.5708, coordinates: '52.6031, 39.5708' },
  { name: 'Киров', lat: 58.6035, lng: 49.6668, coordinates: '58.6035, 49.6668' },
  { name: 'Чебоксары', lat: 56.1324, lng: 47.2519, coordinates: '56.1324, 47.2519' },
  { name: 'Тула', lat: 54.1961, lng: 37.6182, coordinates: '54.1961, 37.6182' },
  { name: 'Калининград', lat: 54.7074, lng: 20.5072, coordinates: '54.7074, 20.5072' },
  { name: 'Курск', lat: 51.7373, lng: 36.1873, coordinates: '51.7373, 36.1873' },
  { name: 'Улан-Удэ', lat: 51.8335, lng: 107.5841, coordinates: '51.8335, 107.5841' },
  { name: 'Ставрополь', lat: 45.0428, lng: 41.9734, coordinates: '45.0428, 41.9734' },
  { name: 'Иваново', lat: 57.0004, lng: 40.9739, coordinates: '57.0004, 40.9739' },
  { name: 'Брянск', lat: 53.2521, lng: 34.3717, coordinates: '53.2521, 34.3717' },
  { name: 'Белгород', lat: 50.5977, lng: 36.5858, coordinates: '50.5977, 36.5858' },
  { name: 'Архангельск', lat: 64.5473, lng: 40.5602, coordinates: '64.5473, 40.5602' },
  { name: 'Владимир', lat: 56.1296, lng: 40.4070, coordinates: '56.1296, 40.4070' },
  { name: 'Севастополь', lat: 44.6166, lng: 33.5254, coordinates: '44.6166, 33.5254' },
  { name: 'Чита', lat: 52.0515, lng: 113.4719, coordinates: '52.0515, 113.4719' },
  { name: 'Грозный', lat: 43.3178, lng: 45.6949, coordinates: '43.3178, 45.6949' },
  { name: 'Смоленск', lat: 54.7818, lng: 32.0401, coordinates: '54.7818, 32.0401' },
  { name: 'Вологда', lat: 59.2239, lng: 39.8839, coordinates: '59.2239, 39.8839' },
  { name: 'Курган', lat: 55.4703, lng: 65.3414, coordinates: '55.4703, 65.3414' },
  { name: 'Орёл', lat: 52.9686, lng: 36.0703, coordinates: '52.9686, 36.0703' },
  { name: 'Владикавказ', lat: 43.0250, lng: 44.6751, coordinates: '43.0250, 44.6751' },
  { name: 'Мурманск', lat: 68.9792, lng: 33.0925, coordinates: '68.9792, 33.0925' },
  { name: 'Якутск', lat: 62.0355, lng: 129.6755, coordinates: '62.0355, 129.6755' },
  { name: 'Петрозаводск', lat: 61.7849, lng: 34.3469, coordinates: '61.7849, 34.3469' },
  { name: 'Сыктывкар', lat: 61.6748, lng: 50.8476, coordinates: '61.6748, 50.8476' },
  { name: 'Нальчик', lat: 43.4997, lng: 43.6079, coordinates: '43.4997, 43.6079' },
  { name: 'Саранск', lat: 54.1838, lng: 45.1749, coordinates: '54.1838, 45.1749' },
  { name: 'Чебоксары', lat: 56.1324, lng: 47.2519, coordinates: '56.1324, 47.2519' },
  { name: 'Йошкар-Ола', lat: 56.6324, lng: 47.8848, coordinates: '56.6324, 47.8848' },
  { name: 'Салехард', lat: 66.5494, lng: 66.6083, coordinates: '66.5494, 66.6083' },
  { name: 'Анадырь', lat: 64.7336, lng: 177.5150, coordinates: '64.7336, 177.5150' }
]);

const filteredCities = ref([...cities.value]);

// Methods
function filterCities(val, update) {
  if (val === '') {
    update(() => {
      filteredCities.value = cities.value;
    });
    return;
  }

  update(() => {
    const needle = val.toLowerCase();
    filteredCities.value = cities.value.filter(
      city => city.name.toLowerCase().indexOf(needle) > -1
    );
  });
}

function onCitySelect(city) {
  if (city) {
    props.onSelect({
      latitude: city.lat,
      longitude: city.lng,
      name: city.name
    });
  }
}
</script>

<style scoped>
.city-selector {
  width: 100%;
}
</style> 