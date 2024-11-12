# -*- coding: utf-8 -*-

import adafruit_dht
import time
import paho.mqtt.client as mqtt
import board
import json

#Sensor Setup
sensor = adafruit_dht.DHT11(board.D4)

#MQTT Setup
mqtt_broker = "192.168.38.89"
topic = "sensor/temperature"

#MQTT Client Setup
client = mqtt.Client()

def on_connect(client,userdata, flags,rc):
    print(f"Connected to MQTT Broker! Return code: {rc}")

client.on_connect = on_connect

client.connect(mqtt_broker)

client.loop_start()

while True:
    try:
        temperature = sensor.temperature
        humidity = sensor.humidity
        
        if temperature is not None and humidity is not None:
            # Skapa en JSON-Struktur
            payload = json.dumps({
                "temperature": round(temperature, 1),
                "humidity": round(humidity,1)
            })
            client.publish(topic, payload)
            print(f"Published: {payload}")
        else:
            print("Misslyckas med att läsa sensordata")
        
        time.sleep(5)
        
    except RuntimeError as error:
        print("Error reading sensor: ", error.args[0])
        time.sleep(2)
    except Exception as error:
        sensor.exit()
        raise error
