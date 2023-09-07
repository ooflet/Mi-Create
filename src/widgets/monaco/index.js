var bridge = null;
var editor = null;

require.config({ paths: { 'vs': 'monaco-editor/min/vs' } });
require(['vs/editor/editor.main'], function () {
    container = document.getElementById('container')
    container.style.height = '100%'
    container.style.width = '100%'
    editor = monaco.editor.create(container, {
        fontFamily: "Courier New",
        automaticLayout: true,
    });
    editor.onDidChangeModelContent((event) => {
        sendToPython("value", editor.getModel().getValue())
    })
    editor.onDidChangeModelLanguage((event) => {
        sendToPython("language", event.newLanguage)
    })
});

function init() {
    sendToPython("value", editor.getModel().getValue());
    sendToPython("language", editor.getModel().getLanguageId());
    sendToPython("theme", editor._themeService._theme.themeName);
}

function sendToPython(name, value) {
    bridge.receive_from_js(name, JSON.stringify(value));
}

function updateFromPython(name, value) {
    var data = JSON.parse(value)
    switch (name) {
        case "value":
            editor.getModel().setValue(data);
            break;
        case "language":
            monaco.editor.setModelLanguage(editor.getModel(), data);
            break;
        case "theme":
            monaco.editor.setTheme(data);
            sendToPython("theme", editor._themeService._theme.themeName);
            break;
    }
}

window.onload = function () {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        bridge = channel.objects.bridge;
        bridge.sendDataChanged.connect(updateFromPython);
        bridge.init();
        init();
    });
}
