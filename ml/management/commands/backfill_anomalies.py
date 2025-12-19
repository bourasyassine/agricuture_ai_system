from django.core.management.base import BaseCommand
from django.db.models import Q

from core.models import AnomalyEvent
from ml.agent_rules import generate_recommendation
from ml.agent_service import run_agent
from ml.anomaly_model import detect_anomaly


class Command(BaseCommand):
    help = "Re-run AI agent for anomalies missing message/recommendation and backfill plot references."

    def handle(self, *args, **options):
        queryset = AnomalyEvent.objects.select_related("reading", "plot").filter(
            Q(message__isnull=True)
            | Q(message__exact="")
            | Q(recommendation__isnull=True)
            | Q(recommendation__exact="")
            | Q(plot__isnull=True)
        )

        updated = 0

        for event in queryset:
            reading = event.reading

            if reading:
                # Refresh anomaly type/severity if missing.
                if not event.anomaly_type or not event.severity:
                    is_anomaly, anomaly_type, severity = detect_anomaly(reading)
                    if is_anomaly:
                        if anomaly_type:
                            event.anomaly_type = anomaly_type
                        if severity:
                            event.severity = severity

                if event.plot_id != getattr(reading, "plot_id", None):
                    event.plot = reading.plot

                recommended_action, explanation = generate_recommendation(event)
            else:
                recommended_action, explanation = None, None

            if not event.message:
                event.message = explanation or "No message generated."

            if not event.recommendation:
                event.recommendation = recommended_action or "No recommendation generated."

            event.save()
            run_agent(event)
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} anomalies."))
