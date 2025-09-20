from django.db import models
from django.utils import timezone

# Create your models here.
class Stage(models.Model):
    name = models.CharField(max_length=100)

    PERFORMANCE_TYPES = (
        ("club", "동아리"),
        ("celebrity", "연예인"),
    )
    type = models.CharField(max_length=20, choices=PERFORMANCE_TYPES, default="club")
    # booth 앱의 Location 모델 참조
    location = models.ForeignKey('booth.Location', on_delete =models.CASCADE, related_name='stages')

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    image_url = models.URLField(blank=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta: 
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
            models.Index(fields=['location']),
            models.Index(fields=['name'])
        ]

    #객체 문자열 표시
    def __str__(self):
        return f"{self.name} @ {self.start_time:%Y-%m-%d %H:%M}"
    
    #실시간 공연상태 정보는 따로 필드 x, 실시간으로 시간 계산 하여 자동반환 되도록
    @property
    def is_active(self) -> bool :
        #현재 시간이 지정 공연시간 내 범위이면 true 반환
        now = timezone.now()
        return self.start_time <= now < self.end_time
    
    