import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
#from influxdb_client.client.write_api import SYNCHRONOUS
import json

# MQTT Inställningar
MQTT_BROKER = "192.168.38.89"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/temperature"

# InfluxDB Inställningar
INFLUXDB_URL = "http://192.168.38.7:8086"
INFLUXDB_TOKEN = "pj0_21_K1rPwd27iyPjM_bLJ5Tiqp5lwv9WFfiIXYUYxntgvdG0701I8asQTjYf7P6JkfZ8DY0TfPoXXMX0Irg=="
INFLUXDB_ORG = "nackademin"
INFLUXDB_BUCKET ="sensor-temp"

# Skapa en kllient för att ansluta till influxDB
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
#write_api = influx_client.write_api(write_options=SYNCHRONOUS)
write_api = influx_client.write_api()

# Callback-funktion när ett MQTT-meddelande tas emot
def on_message(client, userdata, message):
    try:
        # Avkoda och bahandla MQTT-meddelande
        payload = message.payload.decode("utf-8")
        
        # Logga det mottagna meddelandet rå
        print(f"Rådata från MQTT: {payload}")
        
        data = json.loads(payload)
        
        # Logga data
        print(f"Mottagen data från MQTT: {data}")
        
        # Skapa en inflyxDB Point och skicka den till databasen
        point = Point("temperature_sensor")\
                .tag("sensor","sensor_1")\
                .field("temperature",data["temperature"])\
                .field("humidity",data["humidity"])
        
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print("Data skickad till influxDB.")
    
    except json.JSONDecodeError as e:
        print(f"JSON-avkodningsfel: {e}")
    
    except Exception as e:
        print(f"Ett fel uppstod: {e}")

# Skapa en MQTT-klient
mqtt_client = mqtt.Client()

# Anslut callback-funktioner
mqtt_client.on_message = on_message

# Anslut till MQTT-brokern
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

# Prenumerera på MQTT-ämnet
mqtt_client.subscribe(MQTT_TOPIC)

# Starta en evigshetsloop som väntar på meddelade
mqtt_client.loop_forever()