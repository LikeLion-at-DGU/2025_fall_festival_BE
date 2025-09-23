from django.db import models
from django.utils import timezone

# Create your models here.
class Coupon(models.Model):
    booth = models.CharField(max_length=100)
    serial_code = models.CharField(max_length=20, unique=True)
    price = models.IntegerField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        status = "사용됨" if self.is_used else "미사용"
        return f"[쿠폰 {self.id}] {self.price}원 ({status})"

class Game(models.Model):
    user_id = models.CharField(max_length=64)  # 프론트에서 전달받는 ID
    is_started = models.BooleanField(default=False)
    try_times = models.IntegerField(default=0)
    is_end = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "종료" if self.is_end else "진행중"
        coupon_info = f"쿠폰 {self.coupon.id}" if self.coupon else "쿠폰 없음"
        return f"[게임 {self.id}] {status} - {coupon_info} (user: {self.user_id})"