import paho.mqtt.client as mqtt
import ssl
import json
import psycopg2

# Configuración MQTT
MQTT_BROKER = "as21ex07zkwi7-ats.iot.us-east-1.amazonaws.com"
MQTT_PORT = 8883
MQTT_TOPIC = "sensor/jardin/tempSensor01/temperatura"
MQTT_CLIENT_ID = "ec2Subscriber01"

# Certificados (en el mismo directorio que el script)
CA_PATH = "root-CA.crt"
CERT_PATH = "IotCore_v2.cert.pem"
KEY_PATH = "IotCore_v2.private.key"

# Configuración PostgreSQL
DB_HOST = "localhost"
DB_NAME = "sensores"
DB_USER = "sensoruser"
DB_PASSWORD = "miclave123"  

def insertar_en_db(payload):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO temperatura (sensor_id, variable, value, unit, timestamp) VALUES (%s, %s, %s, %s, %s)",
            (payload.get("sensor"), payload.get("variable"), payload.get("value"), payload.get("unit"), payload.get("timestamp"))
        )
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Datos insertados correctamente.")
    except Exception as e:
        print(f"❌ Error al insertar en la DB: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado exitosamente al broker MQTT")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Suscrito al topic: {MQTT_TOPIC}")
    else:
        print(f"❌ Falló la conexión. Código: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"📥 Mensaje recibido en {msg.topic}: {payload}")
        insertar_en_db(payload)
    except Exception as e:
        print(f"❌ Error al procesar el mensaje: {e}")

# MQTT client con protocolo actualizado
client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
client.tls_set(
    ca_certs=CA_PATH,
    certfile=CERT_PATH,
    keyfile=KEY_PATH,
    tls_version=ssl.PROTOCOL_TLSv1_2
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_forever()

