// lightAndFan.js
var lightState = 'off'; // Stan światła
var fanState = 'off'; // Stan wiatraka

// Funkcja do obsługi stanu światła
function handleLightState(data) {
    if (data && data.state) {
        console.log("Stan światła:", data.state);
        if (data.state === 'on') {
            $('#lightButton').text('Wyłącz światło');
            $('#lightIndicator').css('background-color', 'yellow');
            lightState = 'on';
        } else if (data.state === 'off') {
            $('#lightButton').text('Włącz światło');
            $('#lightIndicator').css('background-color', 'black');
            lightState = 'off';
        }
    }
}

// Funkcja do obsługi stanu wiatraka
function handleFanState(data) {
    if (data && data.state) {
        console.log("Stan wiatraka:", data.state);
        if (data.state === 'on') {
            $('#fanButton').text('Wyłącz wiatrak');
            $('#fanIndicator').css({
                'background-color': '#FFC107',
                'animation': 'spin 1s linear infinite'
            });
            fanState = 'on';
        } else if (data.state === 'off') {
            $('#fanButton').text('Włącz wiatrak');
            $('#fanIndicator').css({
                'background-color': '#4CAF50',
                'animation': 'none'
            });
            fanState = 'off';
        }
    }
}

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
