/**
 * Router Configuration
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { getToken } from '@/utils/auth'
import { useUserStore } from '@/store'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

NProgress.configure({ showSpinner: false })

// Route Configuration
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: 'Login', hidden: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/index.vue'),
    redirect: '/projects',
    children: [
      {
        path: 'redirect/:path(.*)',
        name: 'Redirect',
        component: () => import('@/views/redirect/index.vue'),
        meta: { title: 'Redirect', hidden: true },
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/projects/index.vue'),
        meta: { title: 'Project Information', icon: 'Operation', affix: true },
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/projects/Detail.vue'),
        meta: { title: 'Project Details', icon: 'Operation', hidden: true },
      },
      {
        path: 'materials',
        name: 'Materials',
        component: () => import('@/views/materials/index.vue'),
        meta: { title: 'Ingredient Master', icon: 'Box' },
      },
      {
        path: 'fillers',
        name: 'Fillers',
        component: () => import('@/views/fillers/index.vue'),
        meta: { title: 'Mineral Filler Master', icon: 'Box' },
      },
      {
        path: 'formulas',
        name: 'Formulas',
        component: () => import('@/views/formulas/index.vue'),
        meta: { title: 'Formulation Composition', icon: 'List' },
      },
      {
        path: 'test-results',
        name: 'TestResults',
        component: () => import('@/views/test-results/index.vue'),
        meta: { title: 'Results', icon: 'DataAnalysis' },
      },
      {
        path: 'agent',
        name: 'AgentWorkspace',
        component: () => import('@/views/agent/index.vue'),
        meta: { title: 'AI Workspace', icon: 'ChatDotRound' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: 'Profile', icon: 'User', hidden: true },
      },
      {
        path: 'system/roles',
        name: 'SystemRoles',
        component: () => import('@/views/system/roles/index.vue'),
        meta: { title: 'Roles', icon: 'Stamp', requiresAdmin: true },
      },
      {
        path: 'system/logs',
        name: 'SystemLogs',
        component: () => import('@/views/system/logs/index.vue'),
        meta: { title: 'System Logs', icon: 'Document', requiresAdmin: true },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { hidden: true },
  },
]

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// Navigation guards
router.beforeEach((to, from, next) => {
  NProgress.start()

  // Set page title
  document.title = to.meta.title ? `${to.meta.title} - Advanced PhotoPolymer` : 'Advanced - PhotoPolymer Formulation Management DB'

  const token = getToken()

  if (token) {
    // Logged in
    if (to.path === '/login') {
      next({ path: '/' })
    } else {
      // Check if admin permission is required
      if (to.meta.requiresAdmin) {
        const userStore = useUserStore()
        if (userStore.userInfo?.role === 'admin') {
          next()
        } else {
          ElMessage.error('You do not have access permission')
          next(from.path || '/')
        }
      } else {
        next()
      }
    }
  } else {
    // Not logged in
    if (to.path === '/login') {
      next()
    } else {
      next(`/login?redirect=${to.path}`)
    }
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router

