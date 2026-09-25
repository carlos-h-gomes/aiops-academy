import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { App } from './App'
import './assets/styles.css'

const root = document.getElementById('root')

if (!root) {
  throw new Error('Missing #root application mount point')
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    void navigator.serviceWorker.register('/sw.js').catch(() => undefined)
  })
}
