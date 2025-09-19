from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Admin(models.Model):
    class Role(models.TextChoices):
        STAFF = 'Staff', '축제기획단' # 라벨만 축제 기획단으로 변경
        STUCO = 'Stuco', '총학생회' # 총학 Role 추가
        CLUB = 'Club', '동아리'
        MAJOR = 'Major', '학과'
        
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=20)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF,
    )
    
    def __str__(self):
        return f"[{self.id}] {self.name} ({self.get_role_display()}) - {self.code}"
