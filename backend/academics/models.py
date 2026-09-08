from django.db import models
from accounts.models import Student


class Course(models.Model):
    """
    Academic Course offering with code, credits, syllabus description, and instructor.
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique course code (e.g. CS101, DS204)"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(help_text="Course syllabus and overview")
    credits = models.PositiveSmallIntegerField(default=3)
    instructor = models.CharField(max_length=100)
    department = models.CharField(max_length=100, default='Computer Science')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def total_students(self):
        return self.enrollments.filter(status='active').count()

    @property
    def image_slug(self):
        return f"{self.code.lower()}.jpg"


class Enrollment(models.Model):
    """
    Pivot linking a Student to an enrolled Course, tracking status and enrollment date.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    class Meta:
        ordering = ['-enrollment_date']
        unique_together = ('student', 'course')
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'

    def __str__(self):
        return f"{self.student.roll_number} enrolled in {self.course.code} ({self.status})"


class Attendance(models.Model):
    """
    Daily attendance record for a student in a specific course.
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField()
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='present'
    )
    remarks = models.CharField(max_length=150, blank=True, default='')

    class Meta:
        ordering = ['-date']
        unique_together = ('student', 'course', 'date')
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.student.roll_number} - {self.course.code} on {self.date}: {self.status.capitalize()}"
