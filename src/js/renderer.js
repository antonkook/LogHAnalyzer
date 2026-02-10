function createPlot(ctx) {
    const xyValues = [
        {x:50, y:"test"},
        {x:60, y:8},
        {x:70, y:8}
    ];

    // const ctx = document.getElementById("numberLine");

    new Chart(ctx, {
        type: "scatter",
        data: {
            datasets: [{
            data: [
                { x: 1700000000, y: "occupied" },
                { x: 1700000600, y: "unoccupied" }
            ]
            }]
        },
        options: {
            scales: {
            y: {
                type: "category",
                labels: ["unoccupied", "occupied", "unknown"]
            }
            }
        }
    });
    // const plot = new Chart("numberLine", {
    //   type: "scatter",
    //   data: {},
    //   options: {}
    // });

    // const xyValues = [
    //   {x:50, y:7},
    //   {x:60, y:8},
    //   {x:70, y:8},
    //   {x:80, y:9},
    //   {x:90, y:9},
    //   {x:100, y:9},
    //   {x:110, y:10},
    //   {x:120, y:11},
    //   {x:130, y:14},
    //   {x:140, y:14},
    //   {x:150, y:15}
    // ];

    // new Chart("numberLine", {
    //   type: "scatter",
    //   data: {
    //     datasets: [{
    //       pointRadius: 4,
    //       pointBackgroundColor: "rgba(0,0,255,1)",
    //       data: xyValues
    //     }]
    //   },
    //   options:{}
    // });
}

// render 
document.getElementById("open").onclick = () => {
    window.api.openFile()
}

document.getElementById("database").onclick = () => {
    window.api.openDB()
}

document.getElementById("plot").onclick = () => {
    const ctx = document.getElementById("numberLine");
    createPlot(ctx)
}

document.getElementById("unmount").onclick =  () => {
    window.api.closeFile()
}

