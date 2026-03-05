// const { Chart } = require("chart.js")
const { app, BrowserWindow, dialog, ipcMain } = require("electron")
const { spawn } = require("child_process")
const path = require("path");
const fs = require("fs");
var sudo = require('sudo-prompt');

// variables
let backend = null
let port = null // port for communication with backend
let localhostURL = null // url of the localhost with port 
const mountDir = path.join(process.cwd(), "mountpoint")
const personDir = path.join(process.cwd(), "mountpoint/supervisor/homeassistant/.storage/person")
const deviceDir = path.join(process.cwd(), "mountpoint/supervisor/homeassistant/.storage/core.device_registry")

var options = {
  name: 'Electron',
};

// start backend
function startBackend() {
  return new Promise((resolve, reject) => {
    backend = spawn("python", ["src/python/backend.py"])

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
    sudo.exec(`mkdir -p ${mountDir} && mount -o loop ${path} ${mountDir}`, options,
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
    sudo.exec(`umount -R ${mountDir} && rm -r ${mountDir}`, options,
    function(error, stdout, stderr) {
      if (error) throw error;
      console.log('stdout: ' + stdout);
    })
  } catch (err) {
      console.error("closeFile failed:", err)
  }
}

async function getQuery(min_ts, max_ts, checked, filterMore, selected) {
  const res = await fetch(localhostURL + "/use-image", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      min_ts,
      max_ts,
      checked,
      filterMore,
      selected
    }),
  });

  const query = await res.json();

  // modify query by adding person and area 
  assignSensor(query)

  return query
}


function assignSensor(query) {
  const person = JSON.parse(fs.readFileSync(personDir, "utf8"));
  const device = JSON.parse(fs.readFileSync(deviceDir, "utf8"));

  const items = person.data.items
  const devices = device.data.devices

  query.forEach(row => {
    let sensor = ""
    const entityID = row[1]
    const info = JSON.parse(row[2])
    const sensorName = info.friendly_name
    
    if (sensorName) {
      items.forEach(item => {
        const device_trackers = item.device_trackers
        device_trackers.forEach(tracker => {
          if (tracker === entityID) {
            row[1] += " (" + item.name + ")"
          }
        })
      })
      
      devices.forEach(device => {
        if (sensorName.includes(device.name)) {
          if (device.manufacturer != null) {
            sensor += device.manufacturer
          }

          if (device.model != null) {
            sensor += " " + device.model
          }

          if (device.area_id != null) {
            sensor += " (" + device.area_id + ")"
          }
        }
      }) 
      row.push(sensor) 
    }   
  })
}

async function logMessage(toLog) {
  console.log("R: " + toLog)
}

// ipc stuff 
ipcMain.handle("open-file", async () => {
  await openFileAndSend()
})

ipcMain.handle("close-file", async () => {
  await closeFileAndUnmount()
})

ipcMain.handle("get-query", async (event, min_ts, max_ts, checked, filterMore, selected) => {
  return await getQuery(min_ts, max_ts, checked, filterMore, selected)
})

ipcMain.handle("log-message", async (event, toLog) => {
  await logMessage(toLog)
})


// main function
app.whenReady().then(async () => {
  // spawn backend
  await startBackend()
  createWindow()

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })

  app.on("before-quit", () => {
    if (backend) {
        backend.kill();
        backend = null;
    }
});

  app.on("window-all-closed", async (event) => {
    if (process.platform !== "darwin") {
      app.quit()
    }
  })
})
