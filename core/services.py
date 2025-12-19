from core.models import FieldPlot, AnomalyEvent

def get_plot_status(plot):
    last_event = (
        AnomalyEvent.objects
        .filter(reading__plot=plot)
        .order_by("-created_at")
        .first()
    )

    if not last_event:
        return "OK", None

    if last_event.severity == "high":
        return "CRITICAL", last_event
    elif last_event.severity == "medium":
        return "WARNING", last_event

    return "OK", last_event
