const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld("api", {
  openFile: () => ipcRenderer.invoke("open-file"),
  openDB: () => ipcRenderer.invoke("open-database"),
  closeFile: () => ipcRenderer.invoke("close-file"),
})