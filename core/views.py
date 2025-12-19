from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.models import FieldPlot, AnomalyEvent
from core.serializers import FieldPlotSerializer


class FieldPlotViewSet(viewsets.ModelViewSet):
    queryset = FieldPlot.objects.all()
    serializer_class = FieldPlotSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="status")
    def status(self, request):
        """
        Retourne le statut de chaque parcelle (OK / WARNING / CRITICAL)
        basé sur les anomalies récentes.
        """
        plots = FieldPlot.objects.all()
        data = []

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

            data.append({
                "id": plot.id,
                "name": plot.name,
                "size": plot.size,
                "status": status,
            })

        return Response(data)
