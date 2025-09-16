from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = "board"

router = DefaultRouter(trailing_slash=False)
router.register('boards', BoardViewSet, basename='board')
router.register('notices', NoticeViewSet, basename='notice')
router.register('losts', LostViewSet, basename='lost')

urlpatterns = [
    path('', include(router.urls)),
]
