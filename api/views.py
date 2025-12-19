from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.exceptions import ValidationError
from ml.anomaly_model import detect_anomaly
from core.models import AnomalyEvent
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now, timedelta
from core.models import AnomalyEvent


from core.models import SensorReading
from api.serializers import SensorReadingSerializer
from core.models import (
    FarmProfile,
    FieldPlot,
    SensorReading,
    AnomalyEvent,
    AgentRecommendation
)
from api.serializers import (
    FarmProfileSerializer,
    FieldPlotSerializer,
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer
)
from ml.services import run_anomaly_inference, run_batch_inference
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if hasattr(request.user, 'farm') and request.user.farm.role == 'admin':
                return True
        return False

class FarmProfileViewSet(viewsets.ModelViewSet):
    queryset = FarmProfile.objects.all()
    serializer_class = FarmProfileSerializer


class FieldPlotViewSet(viewsets.ModelViewSet):
    queryset = FieldPlot.objects.all()
    serializer_class = FieldPlotSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        farm = serializer.validated_data.get("farm")
        if farm is None:
            farm = getattr(self.request.user, "farm", None)
        if farm is None:
            raise ValidationError({"farm": "A farm profile is required to create a plot."})
        serializer.save(farm=farm)

    @action(detail=False, methods=["get"], url_path="status")
    def status(self, request):
        """
        GET /api/plots/status/
        Retourne le statut de chaque parcelle
        """
        plots = FieldPlot.objects.all()
        result = []

        for plot in plots:
            anomalies = AnomalyEvent.objects.filter(
                reading__plot=plot
            ).order_by("-created_at")

            status = "OK"

            if anomalies.exists():
                severity = anomalies.first().severity
                if severity == "high":
                    status = "CRITICAL"
                elif severity == "medium":
                    status = "WARNING"

            result.append({
                "id": plot.id,
                "name": plot.name,
                "size_hectares": plot.size_hectares,
                "status": status,
            })

        return Response(result)


##week1day6
class SensorReadingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]#permssion
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    
    
    def perform_create(self, serializer):
        reading = serializer.save()  # crée SensorReading en DB

      
    

    def get_queryset(self):
        queryset = SensorReading.objects.all()
        plot_id = self.request.query_params.get("plot")
        if plot_id:
            queryset = queryset.filter(plot_id=plot_id)
        return queryset

    @action(detail=True, methods=["post"], url_path="run-inference")
    def run_inference(self, request, pk=None):
        """
        Trigger ML inference for a single sensor reading.
        """
        reading = self.get_object()
        is_anomaly, event, created = run_anomaly_inference(reading)

        response_data = {"anomaly": is_anomaly}
        if is_anomaly and event:
            response_data["event"] = AnomalyEventSerializer(event).data
            response_data["created"] = created

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="batch-inference")
    def batch_inference(self, request):
        """
        Run inference across a collection of readings (optionally filtered by plot).
        """
        plot_id = request.data.get("plot")
        queryset = self.get_queryset()
        if plot_id:
            queryset = queryset.filter(plot_id=plot_id)

        stats = run_batch_inference(queryset)
        return Response(stats, status=status.HTTP_200_OK)

#trier par date   
class AnomalyEventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = AnomalyEvent.objects.select_related("plot", "reading").order_by('-created_at')
    serializer_class = AnomalyEventSerializer

#trier par dateee
class AgentRecommendationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = AgentRecommendation.objects.all().order_by('-generated_at')
    serializer_class = AgentRecommendationSerializer

#lespermissions
