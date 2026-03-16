// global variables
let chart = null;
let presenceChart = null;

class Point {
    constructor(x, y, info, state, deviceclass, area) {
        this.x = new Date(x.replace(" ", "T"))
        this.y = y
        this.info = info
        this.state = state
        this.deviceclass = deviceclass
        this.area = area
        this.color = this.getColor()
    }

    getColor() {
        let color = "grey"
        switch(this.deviceclass) {
            case "occupancy":
                  color = this.state === "on"  ? "yellow" :
                          this.state === "off" ? "red" :
                                                 "grey"
                break;
            case "door":
                color = this.state === "on"  ? "green" :
                        this.state === "off" ? "green" :
                                               "grey"
                break;
            case "window":
                color = this.state === "on"  ? "green" :
                        this.state === "off" ? "green" :
                                               "grey"
                break;
            case "garage_door":
                color = this.state === "on"  ? "green" :
                        this.state === "off" ? "red" :
                                               "grey"
                break;
            case "lock":
                color = this.state === "on"  ? "green" :
                        this.state === "off" ? "yellow" :
                                               "grey"
                break;
            case "vibration":
                color = this.state === "on"  ? "yellow" :
                        this.state === "off" ? "grey" :
                                               "grey"
                break;
            case "motion":
                color = this.state === "on"  ? "yellow" :
                        this.state === "off" ? "red" :
                                               "grey"
                break;
            // case "humidity":
            //     if (this.state > 70) { // TODO get one of these or find out how it's stored in a different manner?
            //         color = "green"
            //     }
            //     else {
            //         color = "red"
            //     }
            //     break;
            // case "absolute_humidity":

            //     break;
            default:
        } 
        return color
    }
}

class PresencePoint {
    constructor(x, y, trigger, color) {
        this.x = new Date(x.replace(" ", "T"))
        this.y = y
        this.trigger = trigger
        this.color = color
        this.presence = this.getPresence()
    }

    getPresence() {
        return this.color === "green"  ? "human present" :
               this.color === "yellow" ? "human potentially present" :
               this.color === "red"    ? "human not present" :
                                         "unknown"
    }
}


async function render() {
    // setup 
    let min_ts = document.getElementById("from").value
    let max_ts = document.getElementById("to").value
    const checked = document.getElementById("filterBox").checked
    const filterMore = document.getElementById("filterMoreBox").checked
    const selectedObj = document.querySelector('input[name="mode"]:checked');
    const selected = selectedObj ? selectedObj.value : null

    if (min_ts) {
        min_ts = min_ts.replace("T", " ") + ":00"
    }

    if (max_ts) {
        max_ts = max_ts.replace("T", " ") + ":00"
    }
             
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
    const presencePoints = []
    const pointBackgroundColors = []
    const presencePointBackgroundColors = []
    const labels = []
    const presenceLabels = []
    
    let ts
    let entityID
    let info
    let state
    let deviceclass
    let area
    // let trigger
    let presence
    
    query.forEach(line => {
        ts = line[0]
        entityID = line[1]
        info = line[2]
        state = line[3]
        deviceclass = line[4]
        
        area = line[5]
        // trigger = entityID

        if (!labels.includes(entityID)) 
            labels.push(entityID)
        
        if (!presenceLabels.includes(area)) 
            presenceLabels.push(area)

        // create point 
        const point = new Point(ts, entityID, info, state, deviceclass, area)
        points.push(point)
        pointBackgroundColors.push(point.color)

        // create presencePoint
        if (point.color != "grey") {
            const presencePoint = new PresencePoint(ts, area, entityID, point.color)
            presencePoints.push(presencePoint)
            presencePointBackgroundColors.push(point.color)
        }
    })

    
    
    // create sensor chart
    renderSensorChart(unit, tsMin, tsMax, labels, points, pointBackgroundColors)

    // create sensor table
    renderSensorTable(points)

    // create presence chart
    renderPresenceChart(unit, tsMin, tsMax, presenceLabels, presencePoints, presencePointBackgroundColors)

    // create presence table
    renderPresenceTable(presencePoints)
}


function renderSensorChart(unit, tsMin, tsMax, labels, points, presencePointBackgroundColors) {
    // make table visible
    const container = document.getElementById("sensorContainer");
    container.style.display = "block";

    // data
    const data = {
        datasets: [{
            data: points,
            pointBackgroundColor: presencePointBackgroundColors,
            pointBorderColor: presencePointBackgroundColors,
            pointBorderWidth: 2
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
                    labels: labels,
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
                                "Timestamp: " + point.x.toLocaleString(),
                                "EntityID: " + point.y,
                                "Info: " + point.info,
                                "State: " + point.state,
                                "Deviceclass: " + point.deviceclass
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

    const canvas = document.getElementById("numberLine")
    chart = new Chart(canvas, config)
}


function renderPresenceChart(unit, tsMin, tsMax, presenceLabels, presencePoints, pointBackgroundColors) {
    // make table visible
    const container = document.getElementById("presenceContainer");
    container.style.display = "block";

    // data
    const data = {
        datasets: [{
            data: presencePoints,
            pointBackgroundColor: pointBackgroundColors,
            pointBorderColor: pointBackgroundColors,
            pointBorderWidth: 2
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
                    labels: presenceLabels,
                    ticks: {
                        autoskip: false
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const presencePoint = context.raw;

                            return [
                                "Timestamp: " + presencePoint.x.toLocaleString(),
                                "Area: " + presencePoint.y,
                                "Trigger: " + presencePoint.trigger,
                                "Presence: " + presencePoint.presence
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

    if (presenceChart)
        presenceChart.destroy()
    
    const presenceCanvas = document.getElementById("presencePlot")
    presenceChart = new Chart(presenceCanvas, config)
}


function renderSensorTable(points) {
    // make table visible
    const container = document.getElementById("sensorTableContainer");
    container.style.display = "block";

    const tbody = document.querySelector("#queryTable tbody");
    tbody.innerHTML = ""; // clear previous data

    points.forEach(point => {
        const tr = document.createElement("tr");

        const cells = [
            point.x.toLocaleString(),
            point.y,
            point.info,
            point.state,
            point.deviceclass,
        ]

        cells.forEach(cell => {
            const td = document.createElement("td");
            td.textContent = cell;
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });
}


function renderPresenceTable(presencePoints) {
    // make table visible
    const container = document.getElementById("presenceTableContainer");
    container.style.display = "block";

    const tbody = document.querySelector("#presenceTable tbody");
    tbody.innerHTML = ""; // clear previous data

    presencePoints.forEach(point => {
        const tr = document.createElement("tr");

        const cells = [
            point.x.toLocaleString(),
            point.y,
            point.trigger,
            point.presence
        ]

        cells.forEach(cell => {
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
    render()
}

document.getElementById("toggleConfig").onclick =  () => {
    const config = document.getElementById("config");
    config.style.display = config.style.display === "block" ? "none" : "block"
}

document.getElementById("zoomBox").addEventListener("change", (e) => {
    const checked = document.getElementById("zoomBox").checked

    chart.options.plugins.zoom.zoom.mode = checked ? "x" : "xy"
    chart.update()

    presenceChart.options.plugins.zoom.zoom.mode = checked ? "x" : "xy"
    presenceChart.update()
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