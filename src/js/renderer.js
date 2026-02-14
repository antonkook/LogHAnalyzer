// import 'chartjs-adapter-date-fns';

// global variables
let chart = null;


class Point {
    constructor(x, y, state) {
        // convert "2025-12-02 11:09:14"
        // into valid ISO date
        this.x = new Date(x.replace(" ", "T"))
        this.y = y
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

    if (min_ts)
        min_ts = min_ts.replace("T", " ") + ":00"

    if (max_ts)
        max_ts = max_ts.replace("T", " ") + ":00"
        
    const query = await window.api.getQuery(min_ts, max_ts)

    //debug
    // logMessage(query)
    // logMessage(min_ts)

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

    // let i = 0
    query.forEach(line => {
        const ts = line[0]
        const sensor = line[1] // + i
        // i++
        // const info = line[2]
        const state = line[3]

        if (!sensors.includes(sensor)) 
            sensors.push(sensor)
        
        // create point 
        const point = new Point(ts, sensor, state)
        points.push({
            x: point.x,
            y: point.y
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
            // responsive: false,
            // maintainAspectRatio: false, 
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit,
                        // displayFormats: {
                        //     hour: 'MMM DD'
                        // },
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
                zoom: {
                    // pan: {
                    //     enabled: true,
                    //     mode: 'x',   // x, y, or xy
                    // },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x',
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
}

// render 
document.getElementById("open").onclick = () => {
    window.api.openFile()
}

document.getElementById("plot").onclick = () => {
    createPlot()
}

document.getElementById("unmount").onclick =  () => {
    window.api.closeFile()
}

function logMessage(toLog) {
    window.api.logMessage(toLog)
}


// debug
    // const data = {
    //     labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
    //     datasets: [{
    //         label: '# of Votes',
    //         data: [12, 19, 3, 5, 2, 3],
    //         borderWidth: 1
    //     }]
    // }

    // const config = {
    //     type: 'bar',
    //     data,
    //     options: {
    //         scales: {
    //             y: {
    //                 beginAtZero: true,
    //                 ticks: {
    //                     callback: function(value, index) {
    //                         console.log(this.getLabelForValue(index))
    //                     }
    //                 }
    //             }
    //         }
    //     }
    // }

    // new Chart(document.getElementById("numberLine"), config);
