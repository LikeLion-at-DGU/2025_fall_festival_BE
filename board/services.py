# CRUD 중 C, R, U에 해당하는 비즈니스 로직
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import *
from .serializers import *

# @action(detail=False, methods=["GET"])
#   def related(self, request):