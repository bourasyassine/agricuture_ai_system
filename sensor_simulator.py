import math
import random
import time

import requests

# ==========================================
# CONFIGURATION
# ==========================================

API_URL = "http://127.0.0.1:8000/api/sensor-readings/"
PLOTS_URL = "http://127.0.0.1:8000/api/plots/"
TOKEN_URL = "http://127.0.0.1:8000/api/token/"
REFRESH_URL = "http://127.0.0.1:8000/api/token/refresh/"

USERNAME = "agriculture"
PASSWORD = "soasoa"

PLOT_FALLBACK = [1, 2, 3]
PLOT_REFRESH_SECONDS = 5
FREQUENCY_SECONDS = 5

access_token = None
refresh_token = None
plot_profiles = {}
active_plot_ids = []
last_plot_refresh = 0.0


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
    access_token = data.get("access")
    refresh_token = data.get("refresh")
    print("New tokens obtained.")


def refresh_access():
    global access_token, refresh_token
    if not refresh_token:
        get_tokens()
        return

    response = requests.post(REFRESH_URL, json={"refresh": refresh_token})

    if response.status_code == 200:
        access_token = response.json().get("access")
        print("Access token refreshed.")
    else:
        print("Refresh failed, obtaining new tokens...")
        get_tokens()


def build_headers():
    headers = {"Content-Type": "application/json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


# ==========================================
# PLOT DISCOVERY
# ==========================================

def parse_plot_ids(payload):
    if isinstance(payload, dict):
        payload = payload.get("results", [])
    if not isinstance(payload, list):
        return []

    plot_ids = []
    for item in payload:
        if isinstance(item, dict) and isinstance(item.get("id"), int):
            plot_ids.append(item["id"])
    return plot_ids


def fetch_plot_ids():
    response = requests.get(PLOTS_URL, headers=build_headers())

    if response.status_code == 401:
        refresh_access()
        response = requests.get(PLOTS_URL, headers=build_headers())

    if response.status_code != 200:
        print("Failed to fetch plots:", response.text)
        return []

    try:
        return parse_plot_ids(response.json())
    except ValueError:
        return []


def refresh_plots(force=False):
    global active_plot_ids, last_plot_refresh
    now = time.time()
    if not force and (now - last_plot_refresh) < PLOT_REFRESH_SECONDS:
        return active_plot_ids

    last_plot_refresh = now
    plot_ids = fetch_plot_ids()
    if not plot_ids:
        plot_ids = active_plot_ids or PLOT_FALLBACK

    active_plot_ids = sorted(set(plot_ids))
    for plot_id in active_plot_ids:
        ensure_plot_profile(plot_id)
    return active_plot_ids


# ==========================================
# SENSOR GENERATION
# ==========================================

PLOT_PRESETS = (
    {"temp_offset": -2.5, "humidity_offset": -6.0, "soil_offset": -4.0},
    {"temp_offset": 2.0, "humidity_offset": 6.0, "soil_offset": 4.0},
    {"temp_offset": 0.5, "humidity_offset": 0.0, "soil_offset": 0.0},
)


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def preset_for_plot(plot_id):
    mod = plot_id % 3
    if mod == 1:
        return PLOT_PRESETS[0]
    if mod == 2:
        return PLOT_PRESETS[1]
    return PLOT_PRESETS[2]


def ensure_plot_profile(plot_id):
    if plot_id in plot_profiles:
        return

    preset = preset_for_plot(plot_id)
    base_rng = random.Random(plot_id * 1009)
    soil_base = 35 + preset["soil_offset"] + base_rng.uniform(-4.0, 4.0)

    plot_profiles[plot_id] = {
        "rng": random.Random(plot_id * 9176 + 3),
        "temp_offset": preset["temp_offset"] + base_rng.uniform(-1.0, 1.0),
        "humidity_offset": preset["humidity_offset"] + base_rng.uniform(-4.0, 4.0),
        "soil_moisture": clamp(soil_base, 5, 80),
        "rain_chance": clamp(0.04 + base_rng.uniform(-0.015, 0.015), 0.01, 0.08),
        "irrigation_chance": clamp(0.25 + base_rng.uniform(-0.08, 0.08), 0.05, 0.5),
    }


def simulate_temperature(hour):
    return 12 + 10 * math.sin((hour - 6) * math.pi / 12)


def simulate_humidity(temperature, rng):
    base = 70 - (temperature - 20) * 1.2
    return clamp(base + rng.uniform(-5, 5), 20, 95)


def simulate_soil_moisture(moisture, is_rain, is_irrigation, wind, rng):
    evaporation = rng.uniform(0.05, 0.2) + wind * 0.01
    moisture -= evaporation

    if is_irrigation:
        moisture += rng.uniform(3, 7)
    if is_rain:
        moisture += rng.uniform(5, 12)

    return clamp(moisture, 5, 80)


def inject_anomaly(temp, hum, moist, rng):
    """Inject simulated anomalies with 10% probability."""
    if rng.random() >= 0.10:
        return temp, hum, moist

    anomaly_type = rng.choice(["spike", "drop", "drift", "noise"])

    if anomaly_type == "spike":
        temp += rng.uniform(15, 35)
    elif anomaly_type == "drop":
        moist -= rng.uniform(10, 20)
    elif anomaly_type == "drift":
        temp += rng.uniform(0.5, 2)
        hum += rng.uniform(1, 3)
    elif anomaly_type == "noise":
        temp += rng.uniform(-15, 15)
        hum += rng.uniform(-20, 20)
        moist += rng.uniform(-10, 10)

    print(f"ANOMALY INJECTED: {anomaly_type.upper()}")
    return temp, hum, moist


def generate_reading(plot_id, hour):
    profile = plot_profiles[plot_id]
    rng = profile["rng"]

    temp = simulate_temperature(hour) + profile["temp_offset"] + rng.uniform(-0.6, 0.6)
    temp = clamp(temp, -5, 45)

    hum = simulate_humidity(temp, rng) + profile["humidity_offset"] + rng.uniform(-2.5, 2.5)
    hum = clamp(hum, 20, 95)

    wind = rng.uniform(0, 25)
    is_rain = rng.random() < profile["rain_chance"]
    is_irrigation = profile["soil_moisture"] < 20 and rng.random() < profile["irrigation_chance"]

    soil_moisture = simulate_soil_moisture(profile["soil_moisture"], is_rain, is_irrigation, wind, rng)
    profile["soil_moisture"] = soil_moisture

    temp, hum, soil_moisture = inject_anomaly(temp, hum, soil_moisture, rng)

    return temp, hum, soil_moisture


def ensure_unique_values(plot_id, temp, hum, moist, seen):
    signature = (round(temp, 2), round(hum, 2), round(moist, 2))
    if signature not in seen:
        seen.add(signature)
        return temp, hum, moist

    epsilon = 0.01 * ((plot_id % 9) + 1)
    attempts = 0
    while signature in seen and attempts < 10:
        temp += epsilon
        hum += epsilon / 2
        moist += epsilon / 3
        signature = (round(temp, 2), round(hum, 2), round(moist, 2))
        attempts += 1

    seen.add(signature)
    return temp, hum, moist


# ==========================================
# SEND DATA
# ==========================================

def send_sensor_data(plot_id, temp, hum, moist):
    headers = build_headers()

    payload = {
        "soil_moisture": moist,
        "air_temperature": temp,
        "humidity": hum,
        "plot": plot_id,
    }

    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 401:
        print("Token expired, refreshing...")
        refresh_access()
        headers = build_headers()
        response = requests.post(API_URL, json=payload, headers=headers)

    print(f"[PLOT {plot_id}] temp={temp}, hum={hum}, moist={moist} -> Status {response.status_code}")


# ==========================================
# MAIN LOOP
# ==========================================

if __name__ == "__main__":
    print("Starting sensor simulator with per-plot data isolation...")
    get_tokens()

    t = 0
    refresh_plots(force=True)

    while True:
        hour = (t % 144) / 6
        plot_ids = refresh_plots()

        readings_by_plot = {}
        for plot_id in plot_ids:
            readings_by_plot[plot_id] = generate_reading(plot_id, hour)

        seen = set()
        for plot_id in plot_ids:
            temp, hum, moist = readings_by_plot[plot_id]
            temp, hum, moist = ensure_unique_values(plot_id, temp, hum, moist, seen)
            send_sensor_data(plot_id, round(temp, 2), round(hum, 2), round(moist, 2))

        t += 1
        time.sleep(FREQUENCY_SECONDS)
