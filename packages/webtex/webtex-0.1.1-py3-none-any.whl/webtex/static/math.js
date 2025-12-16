const printMath = (text, container) => {
    container.innerHTML = text;
    MathJax.typesetPromise([container]);
}

const addLaTeXBox = (title, text) => {
    const container = document.getElementById("latex-container");
    const titleElement = document.createElement("label")
    const latexElement = document.createElement("div");
    
    if (title.length > 0 && !title.startsWith("__unnamed_")) {
        titleElement.innerHTML = `${title}:`;
        titleElement.setAttribute("class", "latex-title");
        container.appendChild(titleElement);
    }
    
    latexElement.setAttribute("class", "latex-box");
    container.appendChild(latexElement);
    printMath(text, latexElement);
}

const clearLaTeX = () => {
    const container = document.getElementById("latex-container");
    container.innerText = "";
}

const load = (jsonData) => {
    const keys = Object.keys(jsonData);
    clearLaTeX();
    
    if (keys.length == 0) {
        addLaTeXBox("", "No field loaded. Please use the Python module commands to choose what to display here.");
        return;
    }

    for (const key of keys) {
        addLaTeXBox(key, jsonData[key]);
    }
}

const loc = window.location;
const wsProtocol = loc.protocol === 'https:' ? 'wss' : 'ws';
const wsUrl = `${wsProtocol}://${loc.host}/websocket`;

const socket = new WebSocket(wsUrl);
var ready = false;

window.addEventListener('load', function () {
    ready = true;
});

socket.addEventListener('open', () => {
    console.log('WebSocket connected.');
    localStorage.clear()
});

socket.addEventListener('message', (event) => {
    if (ready) {
        try {
            const receivedData = JSON.parse(event.data);
            localStorage.setItem('falcon-data', event.data);
            load(receivedData)
        }
        catch {}
    }
});    