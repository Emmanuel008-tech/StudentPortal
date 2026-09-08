from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student
from .forms import RegistrationForm, LoginForm, StudentProfileUpdateForm


def register_view(request):
    """
    Handle student account registration with linked Student profile creation.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create standard Django User with hashed password
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )

            # Create associated Student profile
            Student.objects.create(
                user=user,
                roll_number=form.cleaned_data['roll_number'],
                department=form.cleaned_data['department'],
                phone=form.cleaned_data.get('phone', '')
            )

            # Automatically log the student in
            login(request, user)
            messages.success(
                request,
                f"Welcome to SkillPulse, {user.first_name or user.username}! Your student profile has been created."
            )
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, "Please correct the errors below to complete your registration.")
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle student login with session persistence.
    Supports login via username or email.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    next_url = request.GET.get('next', 'dashboard:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            # Check if identifier is an email
            username_to_auth = identifier
            if '@' in identifier:
                user_match = User.objects.filter(email__iexact=identifier).first()
                if user_match:
                    username_to_auth = user_match.username

            user = authenticate(request, username=username_to_auth, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                    return redirect(next_url or 'dashboard:dashboard')
                else:
                    messages.error(request, "This account is inactive. Please contact campus support.")
            else:
                messages.error(request, "Invalid username/email or password. Please try again.")
        else:
            messages.error(request, "Please enter both your username/email and password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    """
    Log out the student and redirect to the landing page.
    """
    logout(request)
    messages.info(request, "You have been logged out securely. See you soon!")
    return redirect('landing')


@login_required
def profile_update_view(request):
    """
    Allow the logged-in student to edit their personal bio, phone, and profile avatar.
    """
    student = getattr(request.user, 'student_profile', None)
    if not student:
        # Auto-create if superuser or missing student profile
        student = Student.objects.create(
            user=request.user,
            roll_number=f"USR-{request.user.id:04d}",
            department="Computer Science"
        )

    if request.method == 'POST':
        form = StudentProfileUpdateForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Your student profile has been updated successfully.")
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, "Please fix the errors in your profile details.")
    else:
        form = StudentProfileUpdateForm(instance=student)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'student': student
    })


def staff_login_view(request):
    """
    Dedicated branded login portal for faculty and administrative staff.
    Restricted strictly to users with is_staff=True.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('accounts:staff_dashboard')

    next_url = request.GET.get('next', 'accounts:staff_dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['username'].strip()
            password = form.cleaned_data['password']

            username_to_auth = identifier
            if '@' in identifier:
                user_match = User.objects.filter(email__iexact=identifier).first()
                if user_match:
                    username_to_auth = user_match.username

            user = authenticate(request, username=username_to_auth, password=password)

            if user is not None:
                if not user.is_staff:
                    messages.error(
                        request,
                        "Access denied. This portal is strictly for academic faculty and administrative staff. "
                        "Students must sign in via the Student Portal login."
                    )
                elif not user.is_active:
                    messages.error(request, "This staff account is inactive. Please contact system administration.")
                else:
                    login(request, user)
                    messages.success(
                        request,
                        f"Welcome to Faculty & Staff Administration, {user.first_name or user.username}!"
                    )
                    return redirect(next_url or 'accounts:staff_dashboard')
            else:
                messages.error(request, "Invalid staff username/email or password.")
        else:
            messages.error(request, "Please enter your staff username/email and password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/staff_login.html', {'form': form, 'next': next_url})


def staff_dashboard_view(request):
    """
    Branded staff overview and gateway into administrative tools.
    Requires is_staff privilege.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "Administrative authorization required to access the staff portal.")
        return redirect('accounts:staff_login')

    from academics.models import Course, Enrollment, Attendance

    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.filter(status='active').count()
    total_attendance = Attendance.objects.count()

    recent_students = Student.objects.select_related('user').order_by('-created_at')[:6]
    recent_courses = Course.objects.filter(is_active=True)[:6]

    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_attendance': total_attendance,
        'recent_students': recent_students,
        'recent_courses': recent_courses,
    }
    return render(request, 'accounts/staff_dashboard.html', context)
