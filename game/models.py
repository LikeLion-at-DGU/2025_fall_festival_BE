from django.db import models

# Create your models here.
class SiteCoupon(models.Model):
    price = models.IntegerField()
    is_used = models.BooleanField(default=False)

class Game(models.Model):
    is_end = models.BooleanField(default=False)
    coupon = models.ForeignKey(SiteCoupon, on_delete=models.CASCADE)