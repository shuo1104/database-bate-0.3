/**
 * 路由配置
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { getToken } from '@/utils/auth'
import { useUserStore } from '@/store'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

NProgress.configure({ showSpinner: false })

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录', hidden: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/index.vue'),
    redirect: '/projects',
    children: [
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/projects/index.vue'),
        meta: { title: '项目管理', icon: 'Operation' },
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/projects/Detail.vue'),
        meta: { title: '项目详情', icon: 'Operation', hidden: true },
      },
      {
        path: 'materials',
        name: 'Materials',
        component: () => import('@/views/materials/index.vue'),
        meta: { title: '原料管理', icon: 'Box' },
      },
      {
        path: 'fillers',
        name: 'Fillers',
        component: () => import('@/views/fillers/index.vue'),
        meta: { title: '填料管理', icon: 'Box' },
      },
      {
        path: 'formulas',
        name: 'Formulas',
        component: () => import('@/views/formulas/index.vue'),
        meta: { title: '配方成分管理', icon: 'List' },
      },
      {
        path: 'test-results',
        name: 'TestResults',
        component: () => import('@/views/test-results/index.vue'),
        meta: { title: '测试结果管理', icon: 'DataAnalysis' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人信息', icon: 'User', hidden: true },
      },
      {
        path: 'system/users',
        name: 'SystemUsers',
        component: () => import('@/views/system/users/index.vue'),
        meta: { title: '用户管理', icon: 'User', requiresAdmin: true },
      },
      {
        path: 'system/roles',
        name: 'SystemRoles',
        component: () => import('@/views/system/roles/index.vue'),
        meta: { title: '角色管理', icon: 'Stamp', requiresAdmin: true },
      },
      {
        path: 'system/logs',
        name: 'SystemLogs',
        component: () => import('@/views/system/logs/index.vue'),
        meta: { title: '系统日志', icon: 'Document', requiresAdmin: true },
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

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// 路由守卫
router.beforeEach((to, from, next) => {
  NProgress.start()

  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 光创化物 R&D 配方管理系统` : '光创化物 R&D 配方管理系统'

  const token = getToken()

  if (token) {
    // 已登录
    if (to.path === '/login') {
      next({ path: '/' })
    } else {
      // 检查是否需要管理员权限
      if (to.meta.requiresAdmin) {
        const userStore = useUserStore()
        if (userStore.userInfo?.role === 'admin') {
          next()
        } else {
          ElMessage.error('您没有访问权限')
          next(from.path || '/')
        }
      } else {
        next()
      }
    }
  } else {
    // 未登录
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

