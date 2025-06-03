from chalice import Chalice, Response
import psycopg2
import os

app = Chalice(app_name='api-sensores')

def get_connection():
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS']
    )

# GET /sensors → Lista los IDs únicos de sensores registrados
@app.route('/sensors', methods=['GET'])
def listar_sensores():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT sensor_id FROM temperatura")
        sensores = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return {'sensores': sensores}
    except Exception as e:
        return Response(body={'error': str(e)}, status_code=500)

# GET /sensors/{sensor_id}/events → Lista todos los eventos de ese sensor
@app.route('/sensors/{sensor_id}/events', methods=['GET'])
def eventos_por_sensor(sensor_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT variable, value, unit, timestamp FROM temperatura WHERE sensor_id = %s ORDER BY timestamp DESC",
            (sensor_id,)
        )
        eventos = [
            {'variable': v, 'value': float(val), 'unit': u, 'timestamp': ts.isoformat()}
            for v, val, u, ts in cur.fetchall()
        ]
        cur.close()
        conn.close()
        return {'eventos': eventos}
    except Exception as e:
        return Response(body={'error': str(e)}, status_code=500)

# GET /sensors/{sensor_id}/{variable} → Lista registros de una variable específica
@app.route('/sensors/{sensor_id}/{variable}', methods=['GET'])
def eventos_por_variable(sensor_id, variable):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT value, unit, timestamp FROM temperatura WHERE sensor_id = %s AND variable = %s ORDER BY timestamp DESC",
            (sensor_id, variable)
        )
        datos = [
            {'value': float(val), 'unit': u, 'timestamp': ts.isoformat()}
            for val, u, ts in cur.fetchall()
        ]
        cur.close()
        conn.close()
        return {'datos': datos}
    except Exception as e:
        return Response(body={'error': str(e)}, status_code=500)

# GET /data/latest → Último dato por sensor y variable
@app.route('/data/latest', methods=['GET'])
def ultimos_datos():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT ON (sensor_id, variable)
                sensor_id, variable, value, unit, timestamp
            FROM temperatura
            ORDER BY sensor_id, variable, timestamp DESC
        """)
        resultados = [
            {
                'sensor_id': s,
                'variable': v,
                'value': float(val),
                'unit': u,
                'timestamp': ts.isoformat()
            }
            for s, v, val, u, ts in cur.fetchall()
        ]
        cur.close()
        conn.close()
        return {'ultimos_datos': resultados}
    except Exception as e:
        return Response(body={'error': str(e)}, status_code=500)

