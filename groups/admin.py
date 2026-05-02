from django.contrib import admin

from .models import ExpenseGroup, GroupInvitation, GroupMembership


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0


@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    inlines = [GroupMembershipInline]


@admin.register(GroupInvitation)
class GroupInvitationAdmin(admin.ModelAdmin):
    list_display = ('group', 'email', 'status', 'invited_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('email', 'group__name', 'invited_by__username')

# Register your models here.
