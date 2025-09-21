from django.db import models

# Create your models here.
class SiteCoupon(models.Model):
    price = models.IntegerField()
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        status = "사용됨" if self.is_used else "미사용"
        return f"[쿠폰 {self.id}] {self.price}원 ({status})"

class Game(models.Model):
    user_id = models.CharField(max_length=64)  # 프론트에서 전달받는 ID
    is_started = models.BooleanField(default=False)
    try_times = models.IntegerField(default=0)
    is_end = models.BooleanField(default=False)
    coupon = models.ForeignKey(SiteCoupon, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        status = "종료" if self.is_end else "진행중"
        return f"[게임 {self.id}] {status} - 쿠폰 {self.coupon.id} (user: {self.user_id})"