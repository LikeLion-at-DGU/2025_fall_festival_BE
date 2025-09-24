from rest_framework.throttling import SimpleRateThrottle

# IP 기준 (비인증/인증 공통)
class LikeIPBurstThrottle(SimpleRateThrottle):
    scope = "ip_burst"
    def get_cache_key(self, request, view):
        ident = self.get_ident(request)  # 클라이언트 IP
        return self.cache_format % {"scope": self.scope, "ident": ident}

class LikeIPSustainedThrottle(SimpleRateThrottle):
    scope = "ip_sustained"
    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

# 로그인 유저 기준 (인증된 경우에만 적용)
class LikeUserBurstThrottle(SimpleRateThrottle):
    scope = "user_burst"
    def get_cache_key(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        return self.cache_format % {"scope": self.scope, "ident": str(user.pk)}

class LikeUserSustainedThrottle(SimpleRateThrottle):
    scope = "user_sustained"
    def get_cache_key(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        return self.cache_format % {"scope": self.scope, "ident": str(user.pk)}

# 번역
class TransIPBurstThrottle(SimpleRateThrottle):
    scope = "trans_ip_burst"
    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

class TransIPSustainedThrottle(SimpleRateThrottle):
    scope = "trans_ip_sustained"
    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

class TransUserBurstThrottle(SimpleRateThrottle):
    scope = "trans_user_burst"
    def get_cache_key(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        return self.cache_format % {"scope": self.scope, "ident": str(user.pk)}

class TransUserSustainedThrottle(SimpleRateThrottle):
    scope = "trans_user_sustained"
    def get_cache_key(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        return self.cache_format % {"scope": self.scope, "ident": str(user.pk)}