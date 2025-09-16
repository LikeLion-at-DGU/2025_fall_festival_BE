from django.db import models

# Create your models here.
from polymorphic.models import PolymorphicModel

class Board(PolymorphicModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Notice(Board):
    is_emergency = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    content = models.TextField()


class Lost(Board):
    title = models.CharField(max_length=200)
    content = models.TextField()
    location = models.CharField(max_length=200)