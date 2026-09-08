from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'get_full_name', 'get_email', 'department', 'phone', 'created_at')
    list_filter = ('department', 'created_at')
    search_fields = ('roll_number', 'user__username', 'user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Student Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
