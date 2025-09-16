from django.db import models

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=30)
    latitude = models.FloatField()
    longitude = models.FloatField()

class Category(models.Model):
    name = models.CharField(max_length=30)

class Booth(models.Model):
    name = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_night = models.BooleanField(default=False)
    image_url = models.CharField(max_length=200, blank=True, null=True)
    is_liked = models.BooleanField(default=False)
    
class Menu(models.Model):
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    price = models.IntegerField()
    image_url = models.CharField(max_length=200, blank=True, null=True)
    ingrediant = models.IntegerField()
    sold = models.IntegerField() # 판매량
    
class BoothDetail(models.Model):
    all_table = models.IntegerField()
    usage_table = models.IntegerField()
    can_usage = models.BooleanField(default=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField()