"""
Service helpers to run anomaly inference and persist results.
"""

from typing import Dict, Iterable, Optional

from core.models import AnomalyEvent, SensorReading
from ml.agent_rules import generate_recommendation
from ml.anomaly_model import detect_anomaly
from ml.agent_service import run_agent


def run_anomaly_inference(reading):
    """
    Runs ML anomaly detection and triggers the AI agent if anomaly detected.
    """

    is_anomaly, anomaly_type, severity = detect_anomaly(reading)

    if not is_anomaly:
        return False, None, False

    # Pre-compute recommendation so new anomalies are persisted with message/recommendation/plot.
    temp_event = AnomalyEvent(
        reading=reading,
        plot=getattr(reading, "plot", None),
        anomaly_type=anomaly_type,
        severity=severity,
    )
    recommended_action, explanation_text = generate_recommendation(temp_event)
    default_message = explanation_text or "No message generated."
    default_recommendation = recommended_action or "No recommendation generated."

    try:
        event, created = AnomalyEvent.objects.get_or_create(
            reading=reading,
            defaults={
                "anomaly_type": anomaly_type,
                "severity": severity,
                "plot": getattr(reading, "plot", None),
                "message": default_message,
                "recommendation": default_recommendation,
            }
        )
    except AnomalyEvent.MultipleObjectsReturned:
        event = (
            AnomalyEvent.objects
            .filter(reading=reading)
            .order_by("-created_at")
            .first()
        )
        created = False

    updated_fields = []

    if event.anomaly_type != anomaly_type:
        event.anomaly_type = anomaly_type
        updated_fields.append("anomaly_type")

    if event.severity != severity:
        event.severity = severity
        updated_fields.append("severity")

    # Ensure plot is always set (and correct) on the anomaly.
    plot = getattr(reading, "plot", None)
    if plot is not None and event.plot_id != getattr(plot, "id", None):
        event.plot = plot
        updated_fields.append("plot")

    if not event.message:
        event.message = default_message
        updated_fields.append("message")

    if not event.recommendation:
        event.recommendation = default_recommendation
        updated_fields.append("recommendation")

    if updated_fields:
        event.save(update_fields=updated_fields)

    run_agent(event)

    return True, event, created


def run_batch_inference(readings: Optional[Iterable[SensorReading]] = None) -> Dict[str, int]:
    """
    Run inference across many readings. Useful for backfilling.
    Returns stats on how many anomalies were found/created.
    """

    queryset = readings or SensorReading.objects.all()
    stats = {"total_processed": 0, "anomalies_detected": 0, "events_created": 0}

    for reading in queryset:
        stats["total_processed"] += 1
        is_anomaly, _, created = run_anomaly_inference(reading)
        if is_anomaly:
            stats["anomalies_detected"] += 1
        if created:
            stats["events_created"] += 1

    return stats
