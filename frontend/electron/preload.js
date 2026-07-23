import { contextBridge, ipcRenderer } from 'electron'

console.log('Preload script running...')

contextBridge.exposeInMainWorld('electronAPI', {
  // Backend control
  startBackend: () => ipcRenderer.invoke('start-backend'),
  stopBackend: () => ipcRenderer.invoke('stop-backend'),

  // API proxy (safe from renderer)
  apiRequest: (options) => ipcRenderer.invoke('api-request', options),

  // Example convenience methods
  savePerson: (data) =>
    ipcRenderer.invoke('api-request', {
      method: 'POST',
      endpoint: '/persons',
      body: data,
    }),
  generateChart: (data) =>
    ipcRenderer.invoke('api-request', {
      method: 'POST',
      endpoint: '/chart',
      body: data,
    }),
  listPersons: () =>
    ipcRenderer.invoke('api-request', {
      method: 'GET',
      endpoint: '/persons',
    }),
  showAbout: () => ipcRenderer.send('show-about'),
  quitApp: () => ipcRenderer.send('app-quit'),
})
