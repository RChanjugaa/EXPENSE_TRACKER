from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('expense', 'payer', 'receiver', 'amount', 'status')
    list_filter = ('status',)
    search_fields = ('expense__title', 'payer__username', 'receiver__username')

# Register your models here.
