// ui.js
// Funkcja do zmiany widoku na wykres temperatury
$('#temperatureButton').on('click', function() {
    $('#mainMenu').removeClass('visible').addClass('hidden');
    $('#plotSection').removeClass('hidden').addClass('visible');
    createPlot();  // Tworzymy wykres
});

// Funkcja do powrotu do menu głównego
$('#backToMenuButton').on('click', function() {
    $('#plotSection').removeClass('visible').addClass('hidden');
    $('#humidityPlotSection').removeClass('visible').addClass('hidden');
    $('#mainMenu').removeClass('hidden').addClass('visible');
});

// Zaktualizowanie temperatury (stała wartość na razie)
function updateTemperatureDisplay(value) {
    $('#temperatureDisplay').text(value);
}

// Początkowa temperatura
updateTemperatureDisplay("25°C");

// Funkcja do zmiany widoku na wykres wilgotności
$('#humidityButton').on('click', function() {
    $('#mainMenu').removeClass('visible').addClass('hidden');
    $('#humidityPlotSection').removeClass('hidden').addClass('visible');
    createHumidityPlot();  // Tworzymy wykres
});

// Funkcja do powrotu do menu głównego
$('#backToMenuButtonfromhumidity').on('click', function() {
    $('#humidityPlotSection').removeClass('visible').addClass('hidden');
    $('#plotSection').removeClass('visible').addClass('hidden');
    $('#mainMenu').removeClass('hidden').addClass('visible');
});

// Zaktualizowanie wilgotności
function updateHumidityDisplay(value) {
    $('#humidityDisplay').text(value);
}

// Początkowa wilgotność
updateHumidityDisplay("25%");
