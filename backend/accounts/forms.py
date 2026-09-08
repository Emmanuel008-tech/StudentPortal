from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Student


class RegistrationForm(forms.Form):
    """
    Registration form handling both Django User creation and associated Student profile.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. alexmorgan',
            'autocomplete': 'username',
            'class': 'form-input'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'e.g. alex.morgan@campus.edu',
            'autocomplete': 'email',
            'class': 'form-input'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Alex',
            'class': 'form-input'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Morgan',
            'class': 'form-input'
        })
    )
    roll_number = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. STU-2026-0042',
            'class': 'form-input'
        })
    )
    department = forms.ChoiceField(
        choices=Student.DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. +1 555-019-2834',
            'class': 'form-input'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'At least 8 characters',
            'autocomplete': 'new-password',
            'class': 'form-input'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Re-enter your password',
            'autocomplete': 'new-password',
            'class': 'form-input'
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_roll_number(self):
        roll_number = self.cleaned_data['roll_number'].strip().upper()
        if Student.objects.filter(roll_number__iexact=roll_number).exists():
            raise ValidationError("A student with this roll number is already registered.")
        return roll_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and len(password) < 8:
            self.add_error('password', "Password must be at least 8 characters long.")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please verify.")

        return cleaned_data


class LoginForm(forms.Form):
    """
    Standard login form accepting username and password.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username or Email',
            'autocomplete': 'username',
            'class': 'form-input'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Your secure password',
            'autocomplete': 'current-password',
            'class': 'form-input'
        })
    )


class StudentProfileUpdateForm(forms.ModelForm):
    """
    Form allowing students to update their profile information.
    """
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Student
        fields = ['phone', 'department', 'bio', 'profile_photo']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        student = super().save(commit=False)
        user = student.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            student.save()
        return student
