import React, { useState, useEffect } from 'react';
import mqtt from 'mqtt';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

// Registrera Chart.js komponenter
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

function App() {
    const [temperature, setTemperature] = useState(null);
    const [humidity, setHumidity] = useState(null);
    const [temperatureHistory, setTemperatureHistory] = useState([]);
    const [timeHistory, setTimeHistory] = useState([]);

    useEffect(() => {
        // Anslut till MQTT över WebSocket
        // Webbplatsen laddar över HTTPS, behöver WebSocket-anslutning använda wss:// istället för ws:// som är enkelt HTTP
        const client = mqtt.connect('wss://192.168.38.89/mqtt'); // Nginx använder WebSocket proxy

        client.on('connect', () => {
            console.log("Connected to MQTT broker");
            // Prenumererar Topic från MQTT broker
            client.subscribe('sensor/temperature', (err) => {
                if (err) {
                    console.error('Failed to subscribe to topic:', err);
                }
            });
        });

        client.on('message', (topic, message) => {
            const data = JSON.parse(message.toString());
            setTemperature(data.temperature);
            setHumidity(data.humidity);

            // Uppdatera historik för grafen
            setTemperatureHistory((prev) => [...prev, data.temperature].slice(-20)); // Max 20 senaste värden
            setTimeHistory((prev) => [...prev, new Date().toLocaleTimeString()].slice(-20));
        });

        return () => client.end();
    }, []);

    // Konfiguration för grafen
    const data = {
        labels: timeHistory,
        datasets: [
            {
                label: 'Temperature (°C)',
                data: temperatureHistory,
                fill: false,
                borderColor: 'rgba(75,192,192,1)',
                tension: 0.1,
            },
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Temperature Over Time',
            },
        },
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>IoT Dashboard</h1>
                <h2>Real-Time Sensor Data</h2>
                <p>Temperature: {temperature !== null ? `${temperature} °C` : 'N/A'}</p>
                <p>Humidity: {humidity !== null ? `${humidity} %` : 'N/A'}</p>
                <div style={{ width: '600px', margin: '0 auto' }}>
                    <Line data={data} options={options} />
                </div>
            </header>
        </div>
    );
}

export default App;
