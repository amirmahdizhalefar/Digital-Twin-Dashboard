import numpy as np
import time
from datetime import datetime
import random
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# اتصال به InfluxDB داخل Docker از طریق localhost و پورت 8087
client = InfluxDBClient(
    url="http://localhost:8087",
    token="wxL_ZDwcyLN2v13A1ncNyrJwYSFcSgAdhZLekHELkUWnnUL3_b8Ej04pr-b2e4NdTiRu1m4eyrqI86WC6uxxBA==",
    org="IASBS"
)
write_api = client.write_api(write_options=SYNCHRONOUS)

print("🔥 Cognitive Solar Digital Twin شروع شد – ارسال داده هر 10 ثانیه...\n")

while True:
    now = datetime.utcnow()
    hour = now.hour + now.minute / 60

    # تابش خورشید — شبیه‌سازی Gaussian
    if 5 <= hour <= 19:
        irradiance = max(0, 1100 * np.exp(-((hour - 12.5) ** 2) / 5) + random.uniform(-50, 50))
    else:
        irradiance = 0

    # دمای محیط و دمای سطح سلول
    temp_ambient = 20 + 18 * np.sin((hour - 9) * np.pi / 12) + random.uniform(-4, 4)
    temp_cell = temp_ambient + irradiance * 0.035 + random.uniform(-2, 3)

    # محاسبه توان، ولتاژ، جریان
    if irradiance > 50:
        power = 550 * (irradiance / 1000) * (1 - 0.0038 * (temp_cell - 25)) * random.uniform(0.94, 0.99)
        voltage = 41.5 + random.uniform(-1, 1)
        current = power / voltage if voltage > 0 else 0
    else:
        power = voltage = current = 0.0

    # ساخت رکورد InfluxDB
    point = (
        Point("solar_measurement")
        .tag("location", "Zanjan")
        .tag("system", "Cognitive Digital Twin")
        .field("irradiance", float(round(irradiance, 2)))
        .field("temp_ambient", float(round(temp_ambient, 2)))
        .field("temp_cell", float(round(temp_cell, 2)))
        .field("power_w", float(round(power, 2)))
        .field("voltage_v", float(round(voltage, 2)))
        .field("current_a", float(round(current, 2)))
        .time(now, WritePrecision.NS)
    )

    # ارسال به InfluxDB
    write_api.write(bucket="solar_twin", org="IASBS", record=point)

    print(f"{now.strftime('%H:%M:%S')} | توان: {power:.1f}W | تابش: {irradiance:.0f} W/m² | دمای سلول: {temp_cell:.1f}°C")

    time.sleep(10)
