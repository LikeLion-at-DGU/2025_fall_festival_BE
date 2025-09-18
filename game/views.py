# CI/CD를 확인하기 위한 임시 커밋입니다.

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import F

from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        # 로그인한 사용자인 경우
        if user.is_authenticated:
            # 이미 좋아요를 눌렀다면 취소, 아니면 추가
            if user in post.liked_by.all():
                post.liked_by.remove(user)
                post.likes_count = F('likes_count') - 1
                liked = False
            else:
                post.liked_by.add(user)
                post.likes_count = F('likes_count') + 1
                liked = True
        # 비로그인 사용자인 경우
        else:
            # 프론트에서 중복을 막았다고 가정하고, 카운트만 올림
            post.likes_count = F('likes_count') + 1
            liked = True # 비로그인 유저는 취소가 불가능하므로 항상 true
        
        post.save()
        post.refresh_from_db() # F() 표현식을 사용한 후 최신 값을 가져옴

        return Response({'likes_count': post.likes_count, 'liked': liked})