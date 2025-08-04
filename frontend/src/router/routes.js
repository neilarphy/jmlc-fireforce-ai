import { authGuard, guestGuard } from './middleware'

const routes = [
  {
    path: '/login',
    component: () => import('pages/LoginPage.vue'),
    beforeEnter: guestGuard,
    meta: { requiresAuth: false }
  },
  {
    path: '/test',
    component: () => import('layouts/EmptyLayout.vue'),
    meta: { requiresAuth: false },
    children: [
      { path: '', component: () => import('pages/TestPage.vue') }
    ]
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    beforeEnter: authGuard,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        component: () => import('pages/IndexPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'map',
        component: () => import('pages/MapPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'predictions',
        component: () => import('pages/PredictionsPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'history',
        component: () => import('pages/HistoryPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'alerts',
        component: () => import('pages/AlertsPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'analytics',
        component: () => import('pages/AnalyticsPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'team',
        component: () => import('pages/TeamPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'settings',
        component: () => import('pages/SettingsPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'profile',
        component: () => import('pages/ProfilePage.vue'),
        meta: { requiresAuth: true }
      },
    ],
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
