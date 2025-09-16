from django.db import models

# Create your models here.
class BoothCoupon(models.Model):
    price = models.IntegerField()
    is_used = models.BooleanField(default=False)
    serial_number = models.CharField(max_length=50)
    
class BoothEvent(models.Model):
    title = models.CharField(max_length=50)
    detail = models.TextField()
    coupon = models.ForeignKey(BoothCoupon, on_delete=models.CASCADE)
    start_time = models.DateField()
    end_time = models.DateField()