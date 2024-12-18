// websocket.js
var socket = io.connect(document.domain + ':' + location.port);

socket.on('connect', function() {
    console.log('Połączono z WebSocket!');
});

// Nasłuchujemy na dane przychodzące z WebSocket
socket.on('gr1_new_temperature_data', function(data) {
    console.log("Otrzymano nowe dane:", data);
    
    if (data && data.x !== undefined && data.y !== undefined) {
        Plotly.extendTraces('gr1_temperaturePlot', {
            x: [[data.x]],
            y: [[data.y]]
        }, [0]);
    }
});

// Nasłuchujemy na wiadomości dotyczące światła
socket.on('gr1_light_state', function(data) {
    handleLightState(data);
});

// Nasłuchujemy na wiadomości dotyczące wiatraka
socket.on('gr1_fan_state', function(data) {
    handleFanState(data);
});

// Nasłuchujemy na dane wilgotności
socket.on('gr1_new_humidity_data', function(data) {
    console.log("Otrzymano nowe dane wilgotności:", data);
    if (data && data.x !== undefined && data.y !== undefined) {
        Plotly.extendTraces('gr1_humidityPlot', {
            x: [[data.x]],
            y: [[data.y]]
        }, [0]);
    }
});
