interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  // 在這裡列出你其他的環境變數...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}