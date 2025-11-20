import os
from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi

# --- 🛠️ Configuración de InfluxDB v2 ---
# Usamos 'localhost' si ejecutas el script FUERA del contenedor (Opción A)
URL = "http://localhost:8086"
ORG = "IkerOrg"
BUCKET = "modbus_bucket"
# Usa el token que definiste en docker-compose.yml
TOKEN = "supersecrettoken" 

# --- 📊 Parámetros de la Medición Modbus ---
# Nombre de la medición (del 'name' en [[inputs.modbus]])
MEASUREMENT_NAME = "chiller_sim"
# Campo que quieres leer (ejemplo: 'temp_oat')
FIELD_NAME = "temp_oat" 

print(f"Conectando a InfluxDB en: {URL}...")

try:
    # 1. Inicializar el cliente InfluxDB
    with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
        query_api: QueryApi = client.query_api()

        # 2. Definir la consulta FLUX para obtener el último valor
        flux_query = f'''
        from(bucket: "{BUCKET}")
          |> range(start: -1h) 
          |> filter(fn: (r) => r._measurement == "{MEASUREMENT_NAME}")
          |> filter(fn: (r) => r._field == "{FIELD_NAME}")
          |> last()
        '''

        # 3. Ejecutar la consulta
        result = query_api.query(query=flux_query)

        # 4. Procesar el resultado
        if result and result[0].records:
            record = result[0].records[0]
            timestamp = record.get('_time')
            value = record.get('_value')
            
            print("\n--- ✅ Lectura exitosa desde InfluxDB ---")
            print(f"Medición: **{MEASUREMENT_NAME}**")
            print(f"Campo: **{FIELD_NAME}**")
            print(f"Último valor leído: **{value}**")
            print(f"Marca de tiempo (UTC): {timestamp}")
            print("---------------------------------------")
        else:
            print(f"\n--- ⚠️ No se encontraron datos ---")
            print(f"Verifica que Telegraf esté ejecutándose y el Modbus en 10.100.100.203 esté respondiendo.")
            print("---------------------------------")

except Exception as e:
    print(f"\n--- ❌ Error de conexión o consulta ---")
    print(f"Asegúrate de que InfluxDB esté accesible en {URL}.")
    print(f"Detalle del error: {e}")
    print("---------------------------------------")