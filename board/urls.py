from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

from django.conf.urls.static import static
from django.conf import settings

app_name = "board"

router = DefaultRouter(trailing_slash=False)
router.register('notices', NoticeViewSet, basename='notice')
router.register('losts', LostViewSet, basename='lost')
router.register('', BoardViewSet, basename='board')

urlpatterns = [
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
