<template>
    <q-page class="q-pa-md">
        <div class="row q-col-gutter-md">
            <div class="col-12 col-md-8">
                <q-card>
                    <q-card-section>
                        <div class="text-h6 text-weight-bold">Профиль пользователя</div>
                    </q-card-section>
                    <q-card-section>
                        <q-form @submit="updateProfile" class="q-gutter-md">
                            <q-input filled v-model="profile.name" label="Имя"
                                :rules="[val => !!val || 'Поле обязательно']" />
                            <q-input filled v-model="profile.email" label="Email" type="email" readonly />
                            <q-input filled v-model="profile.organization" label="Организация" />
                            <q-btn label="Сохранить изменения" type="submit" color="primary" :loading="loading" />
                        </q-form>
                    </q-card-section>
                </q-card>
            </div>
            <div class="col-12 col-md-4">
                <q-card>
                    <q-card-section>
                        <div class="text-h6 text-weight-bold">Статистика</div>
                    </q-card-section>
                    <q-card-section>
                        <q-list>
                            <q-item>
                                <q-item-section>
                                    <q-item-label>Прогнозов создано</q-item-label>
                                    <q-item-label caption>{{ stats.predictions }}</q-item-label>
                                </q-item-section>
                            </q-item>
                            <q-item>
                                <q-item-section>
                                    <q-item-label>Дата регистрации</q-item-label>
                                    <q-item-label caption>{{ stats.joinDate }}</q-item-label>
                                </q-item-section>
                            </q-item>
                        </q-list>
                    </q-card-section>
                </q-card>
            </div>
        </div>
    </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useQuasar } from 'quasar';

const $q = useQuasar();

const loading = ref(false);
const profile = ref({
    name: '',
    email: '',
    organization: ''
});
const stats = ref({
    predictions: 0,
    joinDate: ''
});

async function loadProfile() {
    try {
        // Временно используем мок-данные вместо API
        profile.value = {
            name: 'Иван Петров',
            email: 'ivan.petrov@example.com',
            organization: 'МЧС России'
        };
        stats.value.joinDate = new Date().toLocaleDateString();
        stats.value.predictions = Math.floor(Math.random() * 50);
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function updateProfile() {
    loading.value = true;
    try {
        // Временно используем мок-данные вместо API
        await new Promise(resolve => setTimeout(resolve, 1000)); // Имитируем задержку
        
        $q.notify({
            color: 'positive',
            message: 'Профиль обновлен',
            icon: 'check'
        });
    } catch (error) {
        console.error('Error updating profile:', error);
        $q.notify({
            color: 'negative',
            message: 'Ошибка обновления профиля',
            icon: 'error'
        });
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    loadProfile();
});
</script>