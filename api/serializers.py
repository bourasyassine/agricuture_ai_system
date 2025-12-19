from rest_framework import serializers
from core.models import (
    FarmProfile,
    FieldPlot,
    SensorReading,
    AnomalyEvent,
    AgentRecommendation
)

class FarmProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmProfile
        fields = '__all__'


class FieldPlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldPlot
        fields = '__all__'
        extra_kwargs = {
            "farm": {"required": False},
        }


class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = '__all__'


class AnomalyEventSerializer(serializers.ModelSerializer):
    plot = serializers.PrimaryKeyRelatedField(read_only=True)
    metric = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = AnomalyEvent
        fields = [
            "id",
            "plot",
            "reading",
            "anomaly_type",
            "severity",
            "message",
            "recommendation",
            "created_at",
            "metric",
            "value",
        ]

    def get_metric(self, obj):
        a_type = (obj.anomaly_type or "").lower()
        if "temperature" in a_type:
            return "temperature"
        if "humidity" in a_type:
            return "humidity"
        return "soil_moisture"

    def get_value(self, obj):
        reading = getattr(obj, "reading", None)
        if reading is None:
            return None

        metric = self.get_metric(obj)
        if metric == "temperature":
            return reading.air_temperature
        if metric == "humidity":
            return reading.humidity
        return reading.soil_moisture


class AgentRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentRecommendation
        fields = '__all__'
