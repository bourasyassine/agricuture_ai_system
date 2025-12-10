import requests
import time
import math
import random
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

API_URL = "http://127.0.0.1:8000/api/sensor-readings/"
TOKEN_URL = "http://127.0.0.1:8000/api/token/"
REFRESH_URL = "http://127.0.0.1:8000/api/token/refresh/"

USERNAME = "agriculture"
PASSWORD = "soasoa"

PLOTS = [1]
FREQUENCY_SECONDS = 5

access_token = None
refresh_token = None


# ==========================================
# TOKEN MANAGEMENT
# ==========================================

def get_tokens():
    global access_token, refresh_token
    response = requests.post(TOKEN_URL, json={"username": USERNAME, "password": PASSWORD})

    if response.status_code != 200:
        print("Error obtaining tokens:", response.text)
        return

    data = response.json()
    access_token = data["access"]
    refresh_token = data["refresh"]
    print("✔️ New tokens obtained.")


def refresh_access():
    global access_token, refresh_token
    response = requests.post(REFRESH_URL, json={"refresh": refresh_token})

    if response.status_code == 200:
        access_token = response.json()["access"]
        print("✔️ Access token refreshed.")
    else:
        print("❌ Refresh failed, obtaining new tokens...")
        get_tokens()


# ==========================================
# ANOMALY INJECTION
# ==========================================

def inject_anomaly(temp, hum, moist):
    """Inject simulated anomalies with 10% probability."""
    if random.random() >= 0.10:
        return temp, hum, moist  # no anomaly

    anomaly_type = random.choice(["spike", "drop", "drift", "noise"])

    if anomaly_type == "spike":
        temp += random.uniform(15, 35)
    elif anomaly_type == "drop":
        moist -= random.uniform(10, 20)
    elif anomaly_type == "drift":
        temp += random.uniform(0.5, 2)
        hum += random.uniform(1, 3)
    elif anomaly_type == "noise":
        temp += random.uniform(-15, 15)
        hum += random.uniform(-20, 20)
        moist += random.uniform(-10, 10)

    print(f"⚠️ ANOMALY INJECTED: {anomaly_type.upper()}")
    return temp, hum, moist


# ==========================================
# REALISTIC SENSOR GENERATION
# ==========================================

def simulate_temperature(hour):
    return 12 + 10 * math.sin((hour - 6) * math.pi / 12)


def simulate_humidity(temperature):
    base = 70 - (temperature - 20) * 1.2
    return max(20, min(base + random.uniform(-5, 5), 95))


def simulate_soil_moisture(moisture, is_rain, is_irrigation, wind):
    evaporation = random.uniform(0.05, 0.2) + wind * 0.01
    moisture -= evaporation

    if is_irrigation:
        moisture += random.uniform(3, 7)
    if is_rain:
        moisture += random.uniform(5, 12)

    return max(5, min(moisture, 80))


# ==========================================
# SEND DATA
# ==========================================

def send_sensor_data(plot_id, temp, hum, moist):
    global access_token

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "soil_moisture": moist,
        "air_temperature": temp,
        "humidity": hum,
        "plot": plot_id
    }

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 401:
        print("⚠️ Token expired → refreshing...")
        refresh_access()
        headers["Authorization"] = f"Bearer {access_token}"
        response = requests.post(API_URL, json=payload, headers=headers)

    print(f"[PLOT {plot_id}] temp={temp}, hum={hum}, moist={moist} → Status {response.status_code}")


# ==========================================
# MAIN LOOP
# ==========================================

if __name__ == "__main__":
    print("🚀 Starting sensor simulator with anomaly injection...")
    get_tokens()

    t = 0
    soil_moisture = 35

    while True:
        hour = (t % 144) / 6

        temp = simulate_temperature(hour)
        hum = simulate_humidity(temp)
        wind = random.uniform(0, 25)

        is_rain = random.random() < 0.05
        is_irrigation = soil_moisture < 20 and random.random() < 0.3

        soil_moisture = simulate_soil_moisture(soil_moisture, is_rain, is_irrigation, wind)

        # 🔥 inject anomalies HERE (correct position)
        temp, hum, soil_moisture = inject_anomaly(temp, hum, soil_moisture)

        for plot in PLOTS:
            send_sensor_data(plot, round(temp, 2), round(hum, 2), round(soil_moisture, 2))

        t += 1
        time.sleep(FREQUENCY_SECONDS)
