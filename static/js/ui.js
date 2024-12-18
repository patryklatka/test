// ui.js
// Funkcja do zmiany widoku na wykres temperatury
$('#gr1_temperatureButton').on('click', function() {
    $('#mainMenu').removeClass('visible').addClass('hidden');
    $('#gr1_temperaturePlotSection').removeClass('hidden').addClass('visible');
    createPlot();  // Tworzymy wykres
});

// Funkcja do powrotu do menu głównego
$('#gr1_backToMenuButtonFromTemperature').on('click', function() {
    $('#gr1_temperaturePlotSection').removeClass('visible').addClass('hidden');
    $('#gr1_humidityPlotSection').removeClass('visible').addClass('hidden');
    $('#mainMenu').removeClass('hidden').addClass('visible');
});

// Zaktualizowanie temperatury (stała wartość na razie)
function updateTemperatureDisplay(value) {
    $('#gr1_temperatureDisplay').text(value);
}

// Początkowa temperatura
updateTemperatureDisplay("25°C");

// Funkcja do zmiany widoku na wykres wilgotności
$('#gr1_humidityButton').on('click', function() {
    $('#mainMenu').removeClass('visible').addClass('hidden');
    $('#gr1_humidityPlotSection').removeClass('hidden').addClass('visible');
    createHumidityPlot();  // Tworzymy wykres
});

// Funkcja do powrotu do menu głównego
$('#gr1_backToMenuButtonFromHumidity').on('click', function() {
    $('#gr1_humidityPlotSection').removeClass('visible').addClass('hidden');
    $('#gr1_temperaturePlotSection').removeClass('visible').addClass('hidden');
    $('#mainMenu').removeClass('hidden').addClass('visible');
});

// Zaktualizowanie wilgotności
function updateHumidityDisplay(value) {
    $('#gr1_humidityDisplay').text(value);
}

// Początkowa wilgotność
updateHumidityDisplay("25%");
