from django.db import models

# Create your models here.
class BoardCategory(models.Model):
    name = models.CharField(max_length=100)

class Board(models.Model):
    class Category(models.TextChoices):
        NOTICE = 'Notice', '공지사항'
        EVENT = 'Event', '이벤트'
        LOST = 'Lost', '분실물'
        
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_emergency = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(
        max_length=10,
        choices=Category.choices,
        default=Category.NOTICE,
    )