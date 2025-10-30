/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_PORT: string
  readonly VITE_APP_BASE_API: string
  readonly VITE_API_BASE_URL: string
  readonly VITE_LOG_LEVEL: 'NONE' | 'ERROR' | 'WARN' | 'INFO' | 'DEBUG'
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

