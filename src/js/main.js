const { app, BrowserWindow, dialog } = require("electron")
const { spawn } = require("child_process")
const backend = spawn("python", ["src/python/backend.py"])

// variables
let port = null // port for communication with backend
let localhostURL = null // url of the localhost with port 

// start backend
function startBackend() {
  return new Promise((resolve, reject) => {
    const backend = spawn("python", ["src/python/backend.py"]);

    backend.stdout.on("data", d => {
      const msg = d.toString();
      if (msg.startsWith("PORT:")) {
        port = msg.split(":")[1].trim();
        localhostURL = `http://127.0.0.1:${port}`;
        resolve();
      }
    });

    backend.stderr.on("data", d => console.error(d.toString()));
  });
}

// send image path to backend
async function openFileAndSend() {
  try {
    const result = await dialog.showOpenDialog({
      properties: ["openFile"]
    })

    if (result.canceled) return

    const path = result.filePaths[0]

    await fetch(localhostURL + "/use-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path })
    })

  } catch (err) {
      console.error("openFile failed:", err)
  }
}

// create window
function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600
  })

  win.loadFile("src/html/index.html")
}

// main function
app.whenReady().then(async () => {
  await startBackend()
  createWindow()

  // TODO do this after pressing button instead
  await openFileAndSend()

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })

  app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
      app.quit()
    }
  })
})
