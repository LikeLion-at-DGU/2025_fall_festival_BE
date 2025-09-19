from django.db import models

# Create your models here.
class SiteCoupon(models.Model):
    price = models.IntegerField()
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        status = "사용됨" if self.is_used else "미사용"
        return f"[쿠폰 {self.id}] {self.price}원 ({status})"

class Game(models.Model):
    is_end = models.BooleanField(default=False)
    coupon = models.ForeignKey(SiteCoupon, on_delete=models.CASCADE)
    
    def __str__(self):
        status = "종료" if self.is_end else "진행중"
        return f"[게임 {self.id}] {status} - 쿠폰 {self.coupon.id}"