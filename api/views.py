from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission

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

##week1day6
class SensorReadingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]#permssion
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer

    def get_queryset(self):
        queryset = SensorReading.objects.all()
        plot_id = self.request.query_params.get("plot")
        if plot_id:
            queryset = queryset.filter(plot_id=plot_id)
        return queryset

#trier par date   
class AnomalyEventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = AnomalyEvent.objects.all().order_by('-detected_at')
    serializer_class = AnomalyEventSerializer

#trier par dateee
class AgentRecommendationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = AgentRecommendation.objects.all().order_by('-generated_at')
    serializer_class = AgentRecommendationSerializer

#lespermissions

