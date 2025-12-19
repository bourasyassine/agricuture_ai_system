# ml/agent_rules.py

def generate_recommendation(anomaly_event):
    """
    Returns (recommended_action, explanation_text)
    based on anomaly type + severity + reading values.
    """

    reading = anomaly_event.reading
    a_type = anomaly_event.anomaly_type.lower()
    severity = anomaly_event.severity.lower()

    # --- Rule set ---
    if "soil moisture too low" in a_type:
        action = "Start irrigation for this plot and verify the irrigation system."
        explanation = (
            f"Soil moisture is very low ({reading.soil_moisture}%). "
            "This may cause water stress and reduce crop yield. "
            "Irrigation is recommended and the sensor/irrigation lines should be checked."
        )
        return action, explanation

    if "soil moisture too high" in a_type:
        action = "Stop irrigation and check drainage conditions."
        explanation = (
            f"Soil moisture is unusually high ({reading.soil_moisture}%). "
            "This can increase risk of root diseases. "
            "Stop irrigation and inspect drainage / water accumulation."
        )
        return action, explanation

    if "temperature anomaly" in a_type:
        if reading.air_temperature > 40:
            action = "Increase irrigation frequency and consider shading during peak heat."
            explanation = (
                f"Air temperature is extremely high ({reading.air_temperature}°C). "
                "Heat stress can affect plant growth. "
                "Increase irrigation, monitor plants, and consider shading if possible."
            )
        else:
            action = "Protect crops from cold (cover plants) and monitor temperature."
            explanation = (
                f"Air temperature is unusually low ({reading.air_temperature}°C). "
                "Cold stress may damage crops. "
                "Use protective covers and monitor the plot closely."
            )
        return action, explanation

    if "humidity anomaly" in a_type:
        action = "Inspect sensor calibration and monitor for fungal disease risk."
        explanation = (
            f"Humidity is abnormal ({reading.humidity}%). "
            "This may indicate sensor issues or conditions favoring fungal diseases. "
            "Check sensor and monitor crop health."
        )
        return action, explanation

    # default
    action = "Monitor the plot and verify sensor readings."
    explanation = "An anomaly was detected. No specific rule matched; please review the readings."
    return action, explanation
