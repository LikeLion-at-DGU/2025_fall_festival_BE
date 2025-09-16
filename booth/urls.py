from django.urls import path
from .views import BoothDetailAPIView

urlpatterns = [
    path('booths/detail/<int:pk>/', BoothDetailAPIView.as_view(), name='booth-detail'),
]
