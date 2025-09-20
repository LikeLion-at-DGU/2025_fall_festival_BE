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
        name = getattr(self, "name", None) or "Unknown"
        role = self.get_role_display() if hasattr(self, "get_role_display") else "Unknown Role"
        code = getattr(self, "code", "N/A")
        return f"[{getattr(self, 'id', 'N/A')}] {name} ({role}) - {code}"
    
class AdminUID(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name="uids")
    uid = models.CharField(max_length=20, unique=True)
    uid_expires_at = models.DateTimeField()

