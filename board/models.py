from django.db import models
from booth.models import Booth
from adminuser.models import Admin

# Create your models here.
from polymorphic.models import PolymorphicModel

class Board(PolymorphicModel):
    class Category(models.TextChoices):
        NOTICE = 'Notice', '공지'
        LOSTITEM = 'LostItem', '분실물'
        EVENT = 'Event', '이벤트'

    category = models.CharField(
        max_length=10,
        choices=Category.choices,
        default=Category.NOTICE
    )
    writer = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"[{self.id}] {self.get_category_display()} - writer={self.writer}"



#공지
class Notice(Board):
    is_emergency = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    def save(self, *args, **kwargs):
        self.category = Board.Category.NOTICE
        super().save(*args, **kwargs)
    
    def __str__(self):
        flag = "🚨" if self.is_emergency else ""
        return f"[공지] {self.title} {flag}"


#분실물
def image_upload_path(instance, filename):
    return f'board_images/{instance.pk}/{filename}'

class Lost(Board):
    title = models.CharField(max_length=200)
    content = models.TextField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.category = Board.Category.LOSTITEM
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"[분실물] {self.title} ({self.location})"


#event
class BoothEvent(Board):
    title = models.CharField(max_length=50)
    detail = models.TextField()
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE) 
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        self.category = Board.Category.EVENT
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"[이벤트] {self.title} @ {self.booth.name} ({self.start_time} ~ {self.end_time})"
