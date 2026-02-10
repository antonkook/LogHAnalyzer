function createPlot() {
    // setup 
    // const res = await fetch("http://127.0.0.1:PORT/use-image", {
    //     method: "POST"
    // });

    // const query = await res.json();

    // const tsMin = query[0][3]
    // const tsMax = query[query.length - 1][3]

    // query.forEach(line => {
    //     const state     = line[1];
    //     const entityId  = line[2];
    //     const timestamp = line[3];

    //     console.log(entityId, state, timestamp);
    // });

    // setup 
    const data = {
        data: [
            { x: 1, y: "occupied" },
            { x: 2, y: "unoccupied" }
        ]
    }

    const sensors = ["LR_Motion_Sensor", "Joe_MAMA_sensor"]

    // config
    const config = {
        type: "scatter",
        data,
        options: {
            scales: {
                x: {

                },
                y: {
                    type: "category",
                    labels: sensors
                }
            }
        }
    }

    // render
    new Chart(document.getElementById("numberLine"), config);
}

// render 
document.getElementById("open").onclick = () => {
    window.api.openFile()
}

document.getElementById("database").onclick = () => {
    window.api.openDB()
}

document.getElementById("plot").onclick = () => {
    createPlot()
}

document.getElementById("unmount").onclick =  () => {
    window.api.closeFile()
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