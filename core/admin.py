from django.contrib import admin
from .models import SensorReading, AnomalyEvent, FarmProfile, FieldPlot, AgentRecommendation

admin.site.register(SensorReading)
admin.site.register(AnomalyEvent)
admin.site.register(FarmProfile)
admin.site.register(FieldPlot)
admin.site.register(AgentRecommendation)

# Register your models here.
