from django.contrib import admin

from .models import Expense, ExpenseCategory, ExpenseParticipant


class ExpenseParticipantInline(admin.TabularInline):
    model = ExpenseParticipant
    extra = 0


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'amount', 'paid_by', 'category', 'expense_date')
    list_filter = ('category', 'expense_date')
    search_fields = ('title', 'description')
    inlines = [ExpenseParticipantInline]


admin.site.register(ExpenseCategory)

# Register your models here.
