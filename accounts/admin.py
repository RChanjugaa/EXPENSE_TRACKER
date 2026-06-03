from django.contrib import admin

from .models import EmailLoginOTP, EmailVerification


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'verified_at', 'created_at')
    search_fields = ('user__username', 'user__email')


@admin.register(EmailLoginOTP)
class EmailLoginOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'used_at')
    search_fields = ('user__username', 'user__email')

# Register your models here.
