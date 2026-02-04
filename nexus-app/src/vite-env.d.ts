/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_OPEN_WEBUI_URL: string
  readonly VITE_OPEN_WEBUI_API_KEY: string
  readonly VITE_NEXUS_MODEL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
