const { contextBridge, ipcRenderer } = require("electron")

contextBridge.exposeInMainWorld("api", {
  openFile: () => ipcRenderer.invoke("open-file"),
  closeFile: () => ipcRenderer.invoke("close-file"),
  getQuery: (min_ts, max_ts) => ipcRenderer.invoke("get-query", min_ts, max_ts),
  logMessage: (toLog) => ipcRenderer.invoke("log-message", toLog),
})