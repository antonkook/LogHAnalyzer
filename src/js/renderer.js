
document.getElementById("open").onclick = () => {
    window.api.openFile()
}

document.getElementById("database").onclick = () => {
    window.api.openDB()
}

document.getElementById("unmount").onclick =  () => {
    window.api.closeFile()
}
