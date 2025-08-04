<template>
  <q-page class="predictions-page q-pa-lg">
    <!-- Заголовок страницы -->
    <div class="page-header q-mb-xl">
      <div class="text-h4 text-weight-bold text-primary">Прогнозы</div>
      <div class="text-subtitle1 text-grey-6 q-mt-sm">Анализ и прогнозирование пожарной опасности</div>
    </div>

    <div class="row q-col-gutter-xl">
      <!-- Создать прогноз -->
      <div class="col-12 col-lg-4">
        <q-card class="dashboard-card prediction-form-card">
          <q-card-section class="card-header">
            <div class="row items-center">
              <q-icon name="analytics" size="28px" color="primary" class="q-mr-md" />
              <div>
                <div class="text-h6 text-weight-bold">Создать прогноз</div>
                <div class="text-caption text-grey-6">Введите координаты для анализа риска</div>
              </div>
            </div>
          </q-card-section>
          <q-card-section class="card-content">
            <q-form @submit="createPrediction">
              <q-input
                v-model.number="form.latitude"
                label="Широта"
                type="number"
                step="0.0001"
                outlined
                class="q-mb-md form-input"
                :rules="[val => val >= -90 && val <= 90 || 'Введите корректную широту']"
              />
              
              <q-input
                v-model.number="form.longitude"
                label="Долгота"
                type="number"
                step="0.0001"
                outlined
                class="q-mb-md form-input"
                :rules="[val => val >= -180 && val <= 180 || 'Введите корректную долготу']"
              />
              
              <q-btn
                type="submit"
                color="primary"
                label="Создать прогноз"
                :loading="loading"
                class="full-width submit-btn"
                no-caps
                size="lg"
              />
            </q-form>
          </q-card-section>
        </q-card>

        <!-- Результат прогноза -->
        <q-card v-if="currentPrediction" class="dashboard-card result-card q-mt-lg">
          <q-card-section class="card-header">
            <div class="row items-center">
              <q-icon name="trending_up" size="28px" :color="getRiskColor(currentPrediction.risk_level)" class="q-mr-md" />
              <div>
                <div class="text-h6 text-weight-bold">Результат прогноза</div>
                <div class="text-caption text-grey-6">Анализ пожарной опасности</div>
              </div>
            </div>
          </q-card-section>
          <q-card-section class="card-content">
            <div class="text-center q-mb-lg">
              <q-circular-progress
                show-value
                font-size="16px"
                :value="currentPrediction.risk_percentage"
                size="120px"
                :color="getRiskColor(currentPrediction.risk_level)"
                track-color="grey-3"
                class="risk-progress"
              >
                {{ currentPrediction.risk_percentage }}%
              </q-circular-progress>
            </div>
            <div class="text-center">
              <q-badge :color="getRiskColor(currentPrediction.risk_level)" class="risk-badge q-mb-md">
                {{ getRiskLabel(currentPrediction.risk_level) }}
              </q-badge>
              <div class="text-caption text-grey-6">Уверенность: {{ currentPrediction.confidence }}%</div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- История прогнозов -->
      <div class="col-12 col-lg-8">
        <q-card class="dashboard-card history-card">
          <q-card-section class="card-header">
            <div class="row items-center">
              <q-icon name="history" size="28px" color="blue" class="q-mr-md" />
              <div>
                <div class="text-h6 text-weight-bold">История прогнозов</div>
                <div class="text-caption text-grey-6">Ваши предыдущие прогнозы пожарной опасности</div>
              </div>
            </div>
          </q-card-section>
          <q-card-section class="card-content">
            <q-table
              :rows="predictions"
              :columns="columns"
              row-key="id"
              :pagination="pagination"
              :loading="loading"
              class="predictions-table"
              flat
              bordered
            >
              <template v-slot:body-cell-risk_percentage="props">
                <q-td :props="props">
                  <q-circular-progress
                    show-value
                    font-size="10px"
                    :value="props.value"
                    size="50px"
                    :color="getRiskColorByPercentage(props.value)"
                    track-color="grey-3"
                    class="table-progress"
                  >
                    {{ props.value }}%
                  </q-circular-progress>
                </q-td>
              </template>
              <template v-slot:body-cell-confidence="props">
                <q-td :props="props">
                  <q-badge color="blue" class="confidence-badge">{{ props.value }}%</q-badge>
                </q-td>
              </template>
              <template v-slot:body-cell-actions="props">
                <q-td :props="props">
                  <q-btn
                    flat
                    round
                    dense
                    icon="visibility"
                    @click="viewPredictionDetails(props.row)"
                    class="action-btn"
                  />
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Диалог деталей прогноза -->
    <q-dialog v-model="detailsDialog">
      <q-card class="dashboard-card details-dialog" style="min-width: 400px">
        <q-card-section class="card-header">
          <div class="row items-center">
            <q-icon name="info" size="28px" color="primary" class="q-mr-md" />
            <div class="text-h6 text-weight-bold">Детали прогноза #{{ selectedPrediction?.id }}</div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup />
          </div>
        </q-card-section>
        <q-card-section class="card-content" v-if="selectedPrediction">
          <div class="detail-item q-mb-md">
            <div class="text-caption text-grey-6">Координаты</div>
            <div class="text-body1">{{ selectedPrediction.latitude }}, {{ selectedPrediction.longitude }}</div>
          </div>
          <div class="detail-item q-mb-md">
            <div class="text-caption text-grey-6">Риск пожара</div>
            <div class="text-body1">{{ selectedPrediction.risk_percentage }}%</div>
          </div>
          <div class="detail-item q-mb-md">
            <div class="text-caption text-grey-6">Уверенность</div>
            <div class="text-body1">{{ selectedPrediction.confidence }}%</div>
          </div>
          <div class="detail-item q-mb-md">
            <div class="text-caption text-grey-6">Дата создания</div>
            <div class="text-body1">{{ selectedPrediction.created_at }}</div>
          </div>
        </q-card-section>
        <q-card-actions align="right" class="card-content">
          <q-btn flat label="Закрыть" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import ApiService from 'src/services/api';

const $q = useQuasar();

const loading = ref(false);
const detailsDialog = ref(false);
const selectedPrediction = ref(null);
const currentPrediction = ref(null);

const form = ref({
  latitude: 55.7558,
  longitude: 37.6173
});

const predictions = ref([]);

const columns = [
    { name: 'id', label: 'ID', field: 'id', sortable: true, align: 'left' },
    { name: 'created_at', label: 'Дата', field: 'created_at', sortable: true, align: 'left' },
    { name: 'latitude', label: 'Широта', field: 'latitude', sortable: true, align: 'right' },
    { name: 'longitude', label: 'Долгота', field: 'longitude', sortable: true, align: 'right' },
    { name: 'risk_percentage', label: 'Риск', field: 'risk_percentage', sortable: true, align: 'center' },
    { name: 'confidence', label: 'Уверенность', field: 'confidence', sortable: true, align: 'center' },
    { name: 'actions', label: 'Действия', field: 'actions', align: 'center' }
];

const pagination = ref({
    sortBy: 'created_at',
    descending: true,
    page: 1,
    rowsPerPage: 10
});

function getRiskColorByPercentage(percentage) {
    if (percentage < 25) return 'green';
    if (percentage < 50) return 'yellow';
    if (percentage < 75) return 'orange';
    return 'red';
}

function getRiskColor(level) {
    const colors = {
        low: 'green',
        medium: 'yellow', 
        high: 'orange',
        critical: 'red'
    }
    return colors[level] || 'grey'
}

function getRiskLabel(level) {
    const labels = {
        low: 'Низкий риск',
        medium: 'Средний риск',
        high: 'Высокий риск', 
        critical: 'Критический риск'
    }
    return labels[level] || 'Неизвестно'
}

async function createPrediction() {
    try {
        loading.value = true
        
        console.log('Creating prediction with coordinates:', {
            latitude: form.value.latitude,
            longitude: form.value.longitude
        });
        
        // Создаем прогноз через API
        const response = await ApiService.createPrediction({
            latitude: form.value.latitude,
            longitude: form.value.longitude
        });
        
        console.log('Prediction creation response:', response);
        
        // Получаем ID задачи
        const taskId = response.id; // Исправлено: было response.task_id
        
        console.log('Task ID:', taskId);
        
        // Опрашиваем статус до завершения
        let status = response.status;
        let attempts = 0;
        const maxAttempts = 30; // Максимум 30 секунд
        
        while ((status === 'pending' || status === 'processing') && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 1000));
            attempts++;
            
            console.log(`Checking status attempt ${attempts}...`);
            
            const statusResponse = await ApiService.getPredictionStatus(taskId);
            status = statusResponse.status;
            
            console.log('Status response:', statusResponse);
            
            if (statusResponse.result) {
                currentPrediction.value = {
                    id: statusResponse.result.id,
                    latitude: statusResponse.result.latitude,
                    longitude: statusResponse.result.longitude,
                    risk_level: statusResponse.result.risk_level,
                    risk_percentage: statusResponse.result.risk_percentage,
                    confidence: statusResponse.result.confidence,
                    created_at: new Date().toLocaleString()
                };
                break;
            }
        }
        
        if (currentPrediction.value) {
            predictions.value.unshift(currentPrediction.value);
        }
        
        $q.notify({
            color: 'positive',
            message: 'Прогноз успешно создан',
            icon: 'check'
        })
        
    } catch (error) {
        console.error('Error creating prediction:', error)
        $q.notify({
            color: 'negative',
            message: 'Ошибка создания прогноза',
            icon: 'error'
        })
    } finally {
        loading.value = false
    }
}

async function loadPredictions() {
    loading.value = true;
    try {
        const response = await ApiService.getPredictionHistory();
        predictions.value = response || [];
    } catch (error) {
        console.error('Error loading predictions:', error);
        $q.notify({
            color: 'negative',
            message: 'Ошибка загрузки прогнозов',
            icon: 'error'
        });
    } finally {
        loading.value = false;
    }
}

function viewPredictionDetails(prediction) {
    selectedPrediction.value = prediction;
    detailsDialog.value = true;
}

onMounted(() => {
    loadPredictions();
});
</script>

<style lang="scss" scoped>
.predictions-page {
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

.prediction-form-card {
  .form-input {
    border-radius: 12px;
    
    .q-field__control {
      border-radius: 12px;
    }
  }
  
  .submit-btn {
    border-radius: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(37, 99, 235, 0.3);
    }
  }
}

.result-card {
  .risk-progress {
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }
  
  .risk-badge {
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 0.9rem;
  }
}

.history-card {
  .predictions-table {
    border-radius: 12px;
    overflow: hidden;
    
    .q-table__top {
      background: transparent;
    }
    
    .q-table__bottom {
      background: transparent;
    }
  }
  
  .table-progress {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }
  
  .confidence-badge {
    font-weight: 600;
    border-radius: 8px;
    padding: 4px 8px;
  }
  
  .action-btn {
    transition: all 0.2s ease;
    
    &:hover {
      background: rgba(37, 99, 235, 0.1);
      transform: scale(1.1);
    }
  }
}

.details-dialog {
  .detail-item {
    padding: 12px;
    border-radius: 8px;
    background: rgba(37, 99, 235, 0.05);
    transition: all 0.2s ease;
    
    &:hover {
      background: rgba(37, 99, 235, 0.1);
      transform: translateX(4px);
    }
  }
}

// Responsive adjustments
@media (max-width: 768px) {
  .page-header {
    padding: 1rem 0;
    
    .text-h4 {
      font-size: 1.75rem;
    }
  }
  
  .result-card {
    .risk-progress {
      size: 80px;
    }
  }
}
</style>