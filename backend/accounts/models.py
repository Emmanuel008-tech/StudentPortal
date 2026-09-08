from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Student(models.Model):
    """
    Student profile linked one-to-one with Django User.
    Stores roll number, contact details, academic department, and personal bio.
    """
    DEPARTMENT_CHOICES = [
        ('Computer Science', 'Computer Science & Engineering'),
        ('Information Tech', 'Information Technology'),
        ('Data Science', 'Data Science & AI'),
        ('Electrical Eng', 'Electrical & Electronics'),
        ('Mechanical Eng', 'Mechanical Engineering'),
        ('Business Admin', 'Business Administration'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    roll_number = models.CharField(
        max_length=30,
        unique=True,
        help_text="Unique student registration/roll number (e.g. STU-2026-0042)"
    )
    phone = models.CharField(max_length=20, blank=True, default='')
    date_of_birth = models.DateField(null=True, blank=True)
    department = models.CharField(
        max_length=100,
        choices=DEPARTMENT_CHOICES,
        default='Computer Science'
    )
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, default='', max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['roll_number']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        full_name = self.user.get_full_name()
        if full_name:
            return f"{full_name} ({self.roll_number})"
        return f"{self.user.username} ({self.roll_number})"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def initials(self):
        first = self.user.first_name[:1].upper() if self.user.first_name else ''
        last = self.user.last_name[:1].upper() if self.user.last_name else ''
        if not first and not last:
            return self.user.username[:2].upper()
        return f"{first}{last}"

    @property
    def email(self):
        return self.user.email
