// const { Chart } = require("chart.js")
const { app, BrowserWindow, dialog, ipcMain } = require("electron")
const { spawn } = require("child_process")
var sudo = require('sudo-prompt');

// variables
let port = null // port for communication with backend
let localhostURL = null // url of the localhost with port 

var options = {
  name: 'Electron',
};

// start backend
function startBackend() {
  return new Promise((resolve, reject) => {
    const backend = spawn("python", ["src/python/backend.py"])

    backend.stdout.on("data", d => {
      const msg = d.toString();
      console.log("PY:", msg);
      
      if (msg.startsWith("PORT:")) {
        port = msg.split(":")[1].trim();
        localhostURL = `http://127.0.0.1:${port}`;
        resolve();
      }
    });

    backend.stderr.on("data", d => console.error(d.toString()));
  });
}

// create window
function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: __dirname + "/preload.js"
    }
  })

  win.loadFile("src/html/index.html")
}

// send image path to backend
async function openFileAndSend() {
  try {
    const result = await dialog.showOpenDialog({
      properties: ["openFile"]
    })

    if (result.canceled) return

    const path = result.filePaths[0]

    // mount
    sudo.exec(`mkdir -p /mnt/hassos && mount -o loop ${path} /mnt/hassos`, options,
    function(error, stdout, stderr) {
      if (error) throw error;
      console.log('stdout: ' + stdout);
    })

  } catch (err) {
      console.error("openFile failed:", err)
  }
}

async function closeFileAndUnmount() {
  try {
    sudo.exec(`umount -R /mnt/hassos && rm -r /mnt/hassos`, options,
    function(error, stdout, stderr) {
      if (error) throw error;
      console.log('stdout: ' + stdout);
    })
  } catch (err) {
      console.error("closeFile failed:", err)
  }
}

async function getQuery(min_ts, max_ts) {
    const res = await fetch(localhostURL + "/use-image", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            min_ts,
            max_ts,
        }),
    });

    const query = await res.json();
    return query
}

async function logMessage(toLog) {
  console.log(toLog)
}


// ipc stuff 
ipcMain.handle("open-file", async () => {
  await openFileAndSend()
})

ipcMain.handle("close-file", async () => {
  await closeFileAndUnmount()
})

ipcMain.handle("get-query", async (event, min_ts, max_ts) => {
  return await getQuery(min_ts, max_ts)
})

ipcMain.handle("log-message", async (event, toLog) => {
  await logMessage(toLog)
})


// main function
app.whenReady().then(async () => {
  
  await startBackend()
  createWindow()

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })

  app.on("window-all-closed", async (event) => {
    if (process.platform !== "darwin") {
      app.quit()
    }
  })
})
