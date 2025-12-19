# ml/agent_service.py

from core.models import AgentRecommendation
from ml.agent_rules import generate_recommendation

def run_agent(anomaly_event):
    """
    Create/update AgentRecommendation for a given AnomalyEvent.
    """
    action, explanation = generate_recommendation(anomaly_event)

    rec, created = AgentRecommendation.objects.update_or_create(
        anomaly=anomaly_event,
        defaults={
            "recommended_action": action,
            "explanation_text": explanation,
        }
    )
    return rec, created
