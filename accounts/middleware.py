from django.conf import settings
from django.shortcuts import redirect
from django.urls import Resolver404, resolve, reverse


class RequireLoginMiddleware:
    PUBLIC_ROUTE_NAMES = {
        'login',
        'logout',
        'register',
        'verify_email',
        'verify_registration_otp',
        'resend_verification',
        'request_login_otp',
        'verify_login_otp',
    }

    PUBLIC_PREFIXES = (
        '/admin/',
        '/static/',
        '/media/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self.is_public_request(request) or request.user.is_authenticated:
            return self.get_response(request)
        login_url = reverse(settings.LOGIN_URL)
        return redirect(f'{login_url}?next={request.get_full_path()}')

    def is_public_request(self, request):
        if request.path.startswith(self.PUBLIC_PREFIXES):
            return True
        try:
            resolver_match = resolve(request.path_info)
        except Resolver404:
            return False
        if resolver_match.url_name in self.PUBLIC_ROUTE_NAMES:
            return True
        return False
