import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // ============ 公共端（无需登录）============
  {
    path: '/',
    name: 'public-live',
    component: () => import('@/views/public/LiveScreen.vue'),
    meta: { title: '实时动态大屏' },
  },
  {
    path: '/calendar',
    name: 'public-calendar',
    component: () => import('@/views/public/Calendar.vue'),
    meta: { title: '动物出没日历' },
  },
  {
    path: '/rankings',
    name: 'public-rankings',
    component: () => import('@/views/public/Rankings.vue'),
    meta: { title: '趣味排行榜' },
  },
  {
    path: '/guide',
    name: 'public-guide',
    component: () => import('@/views/public/CatGuide.vue'),
    meta: { title: '观测指南' },
  },
  {
    path: '/safety',
    name: 'public-safety',
    component: () => import('@/views/public/SafetyNotice.vue'),
    meta: { title: '安全提醒' },
  },
  {
    path: '/breeds',
    name: 'public-breeds',
    component: () => import('@/views/public/Breeds.vue'),
    meta: { title: '品种百科' },
  },
  {
    path: '/community',
    name: 'public-community',
    component: () => import('@/views/public/Community.vue'),
    meta: { title: '社区分享' },
  },

  // ============ 管理端（需登录）============
  {
    path: '/login',
    name: 'admin-login',
    component: () => import('@/views/admin/Login.vue'),
    meta: { title: '管理员登录' },
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard',
      },
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '管理端总览' },
      },
      {
        path: 'upload',
        name: 'admin-upload',
        component: () => import('@/views/admin/UploadDetect.vue'),
        meta: { title: '上传检测' },
      },
      {
        path: 'records',
        name: 'admin-records',
        component: () => import('@/views/admin/RecordList.vue'),
        meta: { title: '检测记录管理' },
      },
      {
        path: 'safety-tips',
        name: 'admin-safety-tips',
        component: () => import('@/views/admin/SafetyTipMgmt.vue'),
        meta: { title: '安全提醒管理' },
      },
      {
        path: 'export',
        name: 'admin-export',
        component: () => import('@/views/admin/DataExport.vue'),
        meta: { title: '数据导出' },
      },
      {
        path: 'community',
        name: 'admin-community',
        component: () => import('@/views/admin/CommunityMgmt.vue'),
        meta: { title: '社区分享管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：管理端页面未登录 → 跳转 /login
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} · PawVigil`
  }
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    if (!token) {
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
