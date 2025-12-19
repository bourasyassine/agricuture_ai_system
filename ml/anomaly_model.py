# ml/anomaly_model.py

def detect_anomaly(reading):
    """
    Threshold-based anomaly detection.
    Returns tuple (is_anomaly, anomaly_type, severity).
    """

    if reading.air_temperature < 0 or reading.air_temperature > 45:
        return True, "Temperature anomaly", "high"

    if reading.soil_moisture < 10:
        return True, "Soil moisture too low", "medium"

    if reading.soil_moisture > 80:
        return True, "Soil moisture too high", "medium"

    if reading.humidity < 20 or reading.humidity > 95:
        return True, "Humidity anomaly", "low"

    return False, None, None
