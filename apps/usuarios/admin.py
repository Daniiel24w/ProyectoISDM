from django.contrib import admin
from .models import UserActivity

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time')
    list_filter = ('user', 'login_time')
    search_fields = ('user__username',)
    readonly_fields = ('user', 'login_time', 'logout_time')

    def has_add_permission(self, request):
        return False
