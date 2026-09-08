from django.contrib import admin
from .models import Course, Enrollment, Attendance


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    autocomplete_fields = ['student']


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    autocomplete_fields = ['student']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'credits', 'instructor', 'department', 'total_students', 'is_active')
    list_filter = ('department', 'credits', 'is_active')
    search_fields = ('code', 'name', 'instructor', 'description')
    inlines = [EnrollmentInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date', 'status')
    list_filter = ('status', 'enrollment_date', 'course__department')
    search_fields = ('student__roll_number', 'student__user__username', 'course__code', 'course__name')
    autocomplete_fields = ['student', 'course']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'student', 'course', 'status', 'remarks')
    list_filter = ('status', 'date', 'course')
    search_fields = ('student__roll_number', 'student__user__username', 'course__code', 'course__name')
    date_hierarchy = 'date'
    autocomplete_fields = ['student', 'course']
