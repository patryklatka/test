// plot.js
// Funkcja do tworzenia wykresu temperatury
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
            title: 'Temperatura',
            xaxis: { title: 'Czas' },
            yaxis: { title: 'temperatura' }
        }
    };

    Plotly.newPlot('plot', initialData.data, initialData.layout);
}

// Funkcja do tworzenia wykresu wilgotności
function createHumidityPlot() {
    var initialHumidityData = {
        data: [{
            x: [],
            y: [],
            mode: 'lines+markers',
            name: 'Wilgotność',
            hoverinfo: 'text'
        }],
        layout: {
            title: 'Wilgotność',
            xaxis: { title: 'Czas' },
            yaxis: { title: 'Wilgotność (%)' }
        }
    };

    Plotly.newPlot('humidityPlot', initialHumidityData.data, initialHumidityData.layout);
}
