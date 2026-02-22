// global variables
let chart = null;

class Point {
    constructor(x, y, info, state) {
        this.x = new Date(x.replace(" ", "T"))
        this.y = y
        this.info = info
        this.state = state
        this.color = this.getColor()
    }

    getColor() {
        return this.state === "on"  ? "green" :
               this.state === "off" ? "red"   :
                                      "yellow"
    }
}

async function createPlot() {
    // setup 
    min_ts = document.getElementById("from").value
    max_ts = document.getElementById("to").value
    checked = document.getElementById("filterBox").checked
    filterMore = document.getElementById("filterMoreBox").checked
    selectedObj = document.querySelector('input[name="mode"]:checked');
    selected = selectedObj ? selectedObj.value : null

    if (min_ts)
        min_ts = min_ts.replace("T", " ") + ":00"

    if (max_ts)
        max_ts = max_ts.replace("T", " ") + ":00"
        
    const query = await window.api.getQuery(min_ts, max_ts, checked, filterMore, selected)

    if (!query || query.length === 0) return

    // min and max timestamps
    let unit = "day"
    const tsMin = new Date(query[0][0].replace(" ", "T"))
    const tsMax = new Date(query[query.length - 1][0].replace(" ", "T"))
    
    const dateMin = tsMin.toISOString().substring(0, tsMin.toISOString().indexOf("T"))
    const dateMax = tsMax.toISOString().substring(0, tsMax.toISOString().indexOf("T"))

    if (dateMin === dateMax) 
        unit = "hour"
    
        
    // create arrays
    const points = []
    const pointBackgroundColors = []
    const sensors = []

    
    query.forEach(line => {
        const ts = line[0]
        const sensor = line[1]
        const info = line[2]
        const state = line[3]

        if (!sensors.includes(sensor)) 
            sensors.push(sensor)
        
        // create point 
        const point = new Point(ts, sensor, info, state)
        points.push({
            x: point.x,
            y: point.y,
            info,
            state
        })
        pointBackgroundColors.push(point.color)
    });

    const data = {
        datasets: [{
            data: points,
            pointBackgroundColor: pointBackgroundColors,
        }]
    }

    // config
    const config = {
        type: "scatter",
        data,
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit
                    },
                    min: tsMin,
                    max: tsMax,
                },
                y: {
                    type: "category",
                    labels: sensors,
                    ticks: {
                        autoskip: false
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = context.raw;

                            return [
                                "Sensor: " + point.y,
                                "Time: " + point.x.toLocaleString(),
                                "Info: " + point.info,
                                "State: " + point.state
                            ];
                        }
                    }
                },
                zoom: {
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: document.getElementById("zoomBox").checked ? "x" : "xy",
                    }
                }
            }
        }
    }

    // render
    if (chart)
        chart.destroy()

    const canvas = document.getElementById("numberLine");
    chart = new Chart(canvas, config);

    // create table
    renderTable(query)
}


function renderTable(query) {
    // make table visible
    const container = document.getElementById("tableContainer");
    container.style.display = "block";
    // const queryTable = document.getElementById("queryTable")
    // queryTable.style.display = "table"

    const tbody = document.querySelector("#queryTable tbody");
    tbody.innerHTML = ""; // clear previous data

    query.forEach(row => {
        const tr = document.createElement("tr");

        row.forEach(cell => {
            const td = document.createElement("td");
            td.textContent = cell;
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });
}

// render 
document.getElementById("open").onclick = () => {
    window.api.openFile()
}

document.getElementById("unmount").onclick =  () => {
    window.api.closeFile()
}

document.getElementById("plot").onclick = () => {
    createPlot()
}

document.getElementById("toggleConfig").onclick =  () => {
    const config = document.getElementById("config");
    config.style.display = config.style.display === "block" ? "none" : "block"
}

document.getElementById("zoomBox").addEventListener("change", (e) => {
    const checked = document.getElementById("zoomBox").checked
    chart.options.plugins.zoom.zoom.mode = checked ? "x" : "xy"
    chart.update()
});

document.getElementById("filterBox").addEventListener("change", (e) => {
    const filterBox = document.getElementById("filterBox")
    const filterMoreBox = document.getElementById("filterMoreBox");
    filterMoreBox.checked = false
    filterMoreBox.disabled = filterBox.checked ? false : true
});

function logMessage(toLog) {
    window.api.logMessage(toLog)
}