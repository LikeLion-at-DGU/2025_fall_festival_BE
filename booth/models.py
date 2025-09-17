from django.db import models
from django.utils import timezone
from adminuser.models import Admin

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=30)
    latitude = models.FloatField()
    longitude = models.FloatField()
    map_x = models.FloatField()
    map_y = models.FloatField()

class Booth(models.Model):
    class Category(models.TextChoices):
        FOODTRUCK = 'FoodTruck', '푸드트럭'
        TOILET = 'Toilet', '화장실'
        DRINK = 'Drink', '주류판매'
        STORE = 'Store', '편의점'
        BOOTH = 'Booth', '부스'
    
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, default=1)    
    name = models.CharField(max_length=30)
    category = models.CharField(
        max_length=10,
        choices=Category.choices,
        default=Category.BOOTH,
    )
    is_night = models.BooleanField(default=False)
    image_url = models.CharField(max_length=200, blank=True, null=True)
    is_event = models.BooleanField(default=False)
    is_dorder = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    operate_date = models.DateField()
    
    def is_operating_today(self):
        return self.operate_date == timezone.localdate()

    
class BoothDetail(models.Model):
    booth = models.OneToOneField(Booth, on_delete=models.CASCADE)
    all_table = models.IntegerField()
    usage_table = models.IntegerField()
    can_usage = models.BooleanField(default=True)
    description = models.TextField()

class Menu(models.Model):
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    price = models.IntegerField()
    image_url = models.CharField(max_length=200, blank=True, null=True)
    ingredient = models.IntegerField()
    sold = models.IntegerField() # 판매량
    
    
class BoothSchedule(models.Model):
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE)
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
class Like(models.Model):
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    is_liked = models.BooleanField(default=False)