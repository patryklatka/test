var socket = io.connect(document.domain + ':' + location.port);

socket.on('connect', function() {
    console.log('Połączono z WebSocket!');
});

// Nasłuchujemy na dane przychodzące z WebSocket
socket.on('new_data', function(data) {
    console.log("Otrzymano nowe dane:", data);
    
    if (data && data.x !== undefined && data.y !== undefined) {
        Plotly.extendTraces('plot', {
            x: [[data.x]],
            y: [[data.y]]
        }, [0]);
    }
});

// Funkcja do tworzenia wykresu
function createPlot() {
    var initialData = {
        data: [{
            x: [],
            y: [],
            mode: 'lines+markers',
            name: 'Dane',
            hoverinfo: 'text'
        }],
        layout: {
            title: 'Dane z MQTT',
            xaxis: { title: 'X' },
            yaxis: { title: 'Y' }
        }
    };

    Plotly.newPlot('plot', initialData.data, initialData.layout);
}

// Funkcja do zmiany widoku na wykres
$('#temperatureButton').on('click', function() {
    $('#mainMenu').removeClass('visible').addClass('hidden');
    $('#plotSection').removeClass('hidden').addClass('visible');
    createPlot();  // Tworzymy wykres
});

// Funkcja do powrotu do menu głównego
$('#backToMenuButton').on('click', function() {
    $('#plotSection').removeClass('visible').addClass('hidden');
    $('#mainMenu').removeClass('hidden').addClass('visible');
});

// Zaktualizowanie temperatury (stała wartość na razie)
function updateTemperatureDisplay(value) {
    $('#temperatureDisplay').text(value);
}

// Początkowa temperatura
updateTemperatureDisplay("25°C");

// Inicjalizacja pozostałych przycisków
var lightState = 'off'; // Stan światła
var fanState = 'off'; // Stan wiatraka

// Obsługuje kliknięcie w przycisk "Włącz/wyłącz światło"
$('#lightButton').on('click', function() {
    if (lightState === 'off') {
        socket.emit('light_command', { command: 'on' });
        $('#lightButton').text('Wyłącz światło');
        $('#lightIndicator').css('background-color', 'black');
        lightState = 'on';
    } else {
        socket.emit('light_command', { command: 'off' });
        $('#lightButton').text('Włącz światło');
        $('#lightIndicator').css('background-color', 'yellow');
        lightState = 'off';
    }
});

// Obsługuje kliknięcie w przycisk "Włącz/wyłącz wiatrak"
$('#fanButton').on('click', function() {
    if (fanState === 'off') {
        socket.emit('fan_command', { command: 'on' });
        $('#fanButton').text('Wyłącz wiatrak');
        fanState = 'on';
        $('#fanIndicator').css({
            'background-color': '#FFC107',
            'animation': 'spin 1s linear infinite'
        });
    } else {
        socket.emit('fan_command', { command: 'off' });
        $('#fanButton').text('Włącz wiatrak');
        fanState = 'off';
        $('#fanIndicator').css({
            'background-color': '#4CAF50',
            'animation': 'none'
        });
    }
});
