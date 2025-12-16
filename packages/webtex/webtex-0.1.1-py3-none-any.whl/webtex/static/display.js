const lightMode = {
    "--background": "#ffffff",
    "--smooth": "#333333",
    "--scrollbar": "#f1f1f1"
}

const darkMode = {
    "--background": "#333333",
    "--smooth": "#bcbcbc",
    "--scrollbar": "#444444"
}

var currentMode = (typeof webTexConfig != 'undefined') ? webTexConfig['mode'] : 'light';
var title = (typeof webTexConfig != 'undefined') ? webTexConfig['title'] : 'WebTex';

const setMode = (mode) => {
    if (mode != 'light' && mode != 'dark') return;
    theme = mode == 'light' ? lightMode : darkMode;
    let root = document.documentElement;
    for (let key in theme) {
        root.style.setProperty(key, theme[key])
    }
    currentMode = mode;
}

const changeMode = () => {
    let newMode = currentMode == 'light' ? 'dark' : 'light';
    setMode(newMode)
}

const init = () => {
    document.title = title;
    document.getElementById("title").textContent = title;
    setMode(currentMode);
}