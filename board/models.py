from django.db import models
from booth.models import Booth

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


#공지
class Notice(Board):
    is_emergency = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    def save(self, *args, **kwargs):
        self.category = Board.Category.NOTICE
        super().save(*args, **kwargs)


#분실물
class Lost(Board):
    title = models.CharField(max_length=200)
    content = models.TextField()
    location = models.CharField(max_length=200)
    
    def save(self, *args, **kwargs):
        self.category = Board.Category.LOSTITEM
        super().save(*args, **kwargs)

#event
class BoothEvent(Board):
    title = models.CharField(max_length=50)
    detail = models.TextField()
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE) 
    start_time = models.DateField()
    end_time = models.DateField()
    
    def save(self, *args, **kwargs):
        self.category = Board.Category.EVENT
        super().save(*args, **kwargs)
