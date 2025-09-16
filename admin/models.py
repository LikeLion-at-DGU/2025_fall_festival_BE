from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=20)
    is_master = models.BooleanField(default=False)
