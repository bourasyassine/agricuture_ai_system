from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import SensorReading
from ml.services import run_anomaly_inference


@receiver(post_save, sender=SensorReading)
def run_anomaly_detection(sender, instance, created, **kwargs):
    if not created:
        return

    run_anomaly_inference(instance)
