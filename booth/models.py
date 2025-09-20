from django.db import models
from django.utils import timezone
from adminuser.models import Admin


class Location(models.Model):
    name = models.CharField(max_length=30)
    latitude = models.FloatField()
    longitude = models.FloatField()
    map_x = models.FloatField()
    map_y = models.FloatField()
    description = models.CharField(max_length=30, blank=True)
    
    def __str__(self):
        return f"[{self.id}] {self.name} ({self.latitude}, {self.longitude})"


class Booth(models.Model):
    class Category(models.TextChoices):
        FOODTRUCK = 'FoodTruck', '푸드트럭'
        TOILET = 'Toilet', '화장실'
        DRINK = 'Drink', '주류판매'
        STORE = 'Store', '편의점'
        BOOTH = 'Booth', '부스'
    
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, blank=True, null=True)    
    name = models.CharField(max_length=30)
    category = models.CharField(
        max_length=10,
        choices=Category.choices,
        default=Category.BOOTH,
    )
    is_night = models.BooleanField(default=False)
    image_url = models.ImageField(upload_to="booths/images/", blank=True, null=True)
    is_event = models.BooleanField(default=False)
    is_dorder = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    like_cnt = models.IntegerField(default=0)
    
    def __str__(self):
        admin_name = getattr(self.admin, "name", "Unknown Admin")
        booth_name = getattr(self, "name", "Unnamed Booth")
        category = self.get_category_display() if hasattr(self, "get_category_display") else "Unknown Category"
        return f"[{getattr(self, 'id', 'N/A')}] ({booth_name} / {admin_name}) - {category} [event : {self.is_event}]"


    
class BoothDetail(models.Model):
    booth = models.OneToOneField(Booth, on_delete=models.CASCADE)
    all_table = models.IntegerField()
    usage_table = models.IntegerField()
    can_usage = models.BooleanField(default=True)
    description = models.TextField()
    
    def __str__(self):
        return f"[{self.booth.name}] {self.usage_table}/{self.all_table} (usable={self.can_usage})"


class Menu(models.Model):
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    price = models.IntegerField()
    image_url = models.ImageField(upload_to="menus/images/", blank=True, null=True)
    ingredient = models.IntegerField()
    sold = models.IntegerField() # 판매량
    
    def __str__(self):
        return f"[{self.booth.name}] {self.name} - {self.price}원 (sold={self.sold})"


class Corner(models.Model):
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    
    def __str__(self):
        return f"[{self.booth.name}] 코너: {self.name}"

    
class BoothSchedule(models.Model):
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE)
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def __str__(self):
        return f"[{self.booth.name}] {self.day} {self.start_time}~{self.end_time}"

    
class Like(models.Model):
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    is_liked = models.BooleanField(default=False)
    
    def __str__(self):
        status = "❤️" if self.is_liked else "💔"
        return f"[{self.booth.name}] User {self.user_id} {status}"