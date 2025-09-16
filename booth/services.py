from django.shortcuts import get_object_or_404
from .models import Booth

def get_drink_detail(booth_id: int) -> Booth:
    """
    category가 Drink인 booth 상세정보 반환
    """
    booth = get_object_or_404(Booth, id=booth_id)

    if booth.category != Booth.Category.DRINK:
        raise ValueError("요청한 부스의 카테고리가 주류 판매가 아님")

    return booth



def get_toilet_detail(booth_id: int) -> Booth:
    """
    category가 Toilet인 booth 상세정보 반환
    """
    booth = get_object_or_404(Booth, id=booth_id)

    if booth.category != Booth.Category.TOILET:
        raise ValueError("요청한 부스의 카테고리가 화장실이 아님")

    return booth
