# sensor_light.py

import paho.mqtt.client as mqtt
import ssl
import time
import json
import random

ENDPOINT = "as21ex07zkwi7-ats.iot.us-east-1.amazonaws.com"
PORT = 8883
CLIENT_ID = "tempSensor01"
TOPIC = "sensor/jardin/tempSensor01/temperatura"

CA_PATH = "connect_device_package/root-CA.crt"
CERT_PATH = "connect_device_package/IotCore_v2.cert.pem"
KEY_PATH = "connect_device_package/IotCore_v2.private.key"

def on_connect(client, userdata, flags, rc):
    print(f"Conectado con código {rc}")

client = mqtt.Client(client_id=CLIENT_ID)
client.tls_set(ca_certs=CA_PATH,
               certfile=CERT_PATH,
               keyfile=KEY_PATH,
               cert_reqs=ssl.CERT_REQUIRED,
               tls_version=ssl.PROTOCOL_TLSv1_2)

client.on_connect = on_connect
print("Conectando al broker...")
client.connect(ENDPOINT, PORT)
client.loop_start()

while True:
    payload = {
        "sensor": CLIENT_ID,
        "variable": "luz",
        "value": round(random.uniform(200.0, 1000.0), 1),
        "unit": "lux",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    print("Publicando:", payload)
    client.publish(TOPIC, json.dumps(payload), qos=1)
    time.sleep(5)
