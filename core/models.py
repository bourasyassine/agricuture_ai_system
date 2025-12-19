from django.db import models
from django.contrib.auth.models import User


# ------------- FARM PROFILE -------------
class FarmProfile(models.Model):
    #permission hasb role
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('farmer', 'Farmer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="farm")
    farm_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    #role bech nfar9ou bin l'admin w l'farmer
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')

    def __str__(self):
        return self.farm_name


# ------------- FIELD PLOT -------------
class FieldPlot(models.Model):
    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name="plots")
    name = models.CharField(max_length=100)
    size_hectares = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.farm.farm_name})"


# ------------- SENSOR READING -------------
class SensorReading(models.Model):
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name="readings")
    timestamp = models.DateTimeField(auto_now_add=True)

    # Sensor values
    soil_moisture = models.FloatField()
    air_temperature = models.FloatField()
    humidity = models.FloatField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.plot.name} - {self.timestamp}"


# ------------- ANOMALY EVENT -------------
class AnomalyEvent(models.Model):
    reading = models.ForeignKey(SensorReading, on_delete=models.CASCADE, related_name="anomalies")
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name="anomaly_events", null=True, blank=True)
    anomaly_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20)
    message = models.TextField(blank=True, default="")
    recommendation = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["reading"], name="unique_anomaly_per_reading"),
        ]

    def __str__(self):
        plot_name = getattr(self.plot, "name", None) or getattr(self.reading.plot, "name", "Unknown plot")
        return f"{plot_name} - {self.anomaly_type} ({self.severity})"


# ------------- AGENT RECOMMENDATION -------------
class AgentRecommendation(models.Model):
    anomaly = models.OneToOneField(AnomalyEvent, on_delete=models.CASCADE, related_name="agent_recommendation")
    recommended_action = models.TextField()
    explanation_text = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.anomaly.id}"
