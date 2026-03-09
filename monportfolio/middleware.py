import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.http import JsonResponse

logger = logging.getLogger("monportfolio.security")
activity_logger = logging.getLogger("monportfolio.activity")


def parse_browser(user_agent: str) -> str:
    ua = (user_agent or "").lower()
    if "edg/" in ua:
        return "Microsoft Edge"
    if "opr/" in ua or "opera" in ua:
        return "Opera"
    if "chrome/" in ua and "edg/" not in ua:
        return "Chrome"
    if "safari/" in ua and "chrome/" not in ua:
        return "Safari"
    if "firefox/" in ua:
        return "Firefox"
    if "msie" in ua or "trident/" in ua:
        return "Internet Explorer"
    return "Unknown"


def parse_os(user_agent: str) -> str:
    ua = (user_agent or "").lower()
    if "windows nt" in ua:
        return "Windows"
    if "mac os x" in ua or "macintosh" in ua:
        return "macOS"
    if "android" in ua:
        return "Android"
    if "iphone" in ua or "ipad" in ua or "ios" in ua:
        return "iOS"
    if "linux" in ua:
        return "Linux"
    return "Unknown"


class SecurityHeadersMiddleware:
    """Apply additional response headers that are not fully covered by defaults."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        csp = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: blob:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "object-src 'none'"
        )

        response.setdefault("Content-Security-Policy", csp)
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("X-Frame-Options", "DENY")
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.setdefault("X-XSS-Protection", "1; mode=block")

        return response


class ActivityLogMiddleware:
    """Persist visitor activity for each page request."""

    SKIP_PREFIXES = ("/static/", "/media/", "/favicon.ico")
    SKIP_PATHS = {"/activity/time-spent/"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if self._should_skip(request):
            return response

        try:
            from .models import VisitorLog

            if not request.session.session_key:
                request.session.save()

            user_agent = request.META.get("HTTP_USER_AGENT", "")
            ip_address = RateLimitMiddleware._client_ip(request)
            user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None

            log = VisitorLog.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                browser=parse_browser(user_agent),
                os=parse_os(user_agent),
                path=request.path,
                method=request.method,
                session_id=request.session.session_key or "",
            )
            response["X-Visitor-Log-Id"] = str(log.id)
        except Exception as exc:
            activity_logger.warning("Failed to persist visitor log: %s", exc)

        return response

    def _should_skip(self, request):
        if request.path in self.SKIP_PATHS:
            return True
        if request.path.startswith(self.SKIP_PREFIXES):
            return True
        if request.method.upper() in {"OPTIONS", "HEAD"}:
            return True
        return False


class RateLimitMiddleware:
    """Simple per-IP (and optional per-username) rate limiting for sensitive paths."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        limit_name = self._match_limit(request)
        if limit_name:
            blocked_response = self._enforce_limit(request, limit_name)
            if blocked_response is not None:
                return blocked_response

        return self.get_response(request)

    def _match_limit(self, request):
        request_path = request.path
        method = request.method.upper()
        for name, rule in getattr(settings, "RATE_LIMITS", {}).items():
            methods = rule.get("methods", {"GET", "POST"})
            if method not in methods:
                continue

            exact_path = rule.get("path")
            path_prefix = rule.get("path_prefix")

            if exact_path and request_path == exact_path:
                return name
            if path_prefix and request_path.startswith(path_prefix):
                return name

        return None

    def _enforce_limit(self, request, limit_name):
        rule = settings.RATE_LIMITS[limit_name]
        limit = int(rule.get("limit", 60))
        window = int(rule.get("window_seconds", 60))
        ip = self._client_ip(request)

        ip_key = f"rl:{limit_name}:ip:{ip}"
        ip_count = self._increment_key(ip_key, window)

        user_count = 0
        username = ""
        if request.path.endswith("/login/"):
            username = (request.POST.get("username") or "").strip().lower()
            if username:
                user_key = f"rl:{limit_name}:user:{username}"
                user_count = self._increment_key(user_key, window)

        if ip_count > limit or user_count > limit:
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "path": request.path,
                    "ip": ip,
                    "username": username,
                    "limit_name": limit_name,
                    "limit": limit,
                    "window": window,
                },
            )
            return self._too_many_requests_response(request)

        return None

    @staticmethod
    def _increment_key(key, timeout):
        if cache.get(key) is None:
            cache.set(key, 1, timeout=timeout)
            return 1

        try:
            return cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout=timeout)
            return 1

    @staticmethod
    def _client_ip(request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")

    @staticmethod
    def _too_many_requests_response(request):
        retry_after_seconds = "60"
        if request.path.startswith("/api/"):
            response = JsonResponse({"detail": "Too many requests. Try again later."}, status=429)
        else:
            response = HttpResponse("Trop de tentatives. Reessayez plus tard.", status=429)

        response["Retry-After"] = retry_after_seconds
        return response
