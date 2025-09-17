from django.db import models

# Create your models here.
class Stage(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)  #필요한가
    # booth 앱의 Location 모델 참조
    location = models.ForeignKey('booth.Location', on_delete =models.CASCADE, related_name='stages')
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image_url = models.URLField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta: 
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
            models.Index(fields=['location']),
            models.Index(fields=['is_active']),
            models.Index(fields=['name'])
        ]