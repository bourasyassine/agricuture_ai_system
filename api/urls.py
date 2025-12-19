from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import FieldPlotViewSet

router = DefaultRouter()
router.register(r'plots', FieldPlotViewSet, basename='plots')

urlpatterns = [
    path("", include(router.urls)),
]
