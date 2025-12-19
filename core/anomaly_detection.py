# core/anomaly_detection.py

def detect_anomaly(reading):
    """
    Simple threshold-based anomaly detection.
    Returns (is_anomaly, anomaly_type, severity)
    """

    # THRESHOLDS (agriculture realistic)
    if reading.air_temperature < 0 or reading.air_temperature > 45:
        return True, "Temperature anomaly", "high"

    if reading.soil_moisture < 10:
        return True, "Soil moisture too low", "medium"

    if reading.soil_moisture > 80:
        return True, "Soil moisture too high", "medium"

    if reading.humidity < 20 or reading.humidity > 95:
        return True, "Humidity anomaly", "low"

    return False, None, None
#Maintenant, chaque fois qu’un SensorReading est créé, on veut :

#appeler detect_anomaly

#
# si anomalie → créer un AnomalyEvent