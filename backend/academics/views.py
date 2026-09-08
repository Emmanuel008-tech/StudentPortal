from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from accounts.models import Student
from .models import Course, Enrollment, Attendance


def course_list_view(request):
    """
    List all available campus courses and current enrollment status.
    Publicly accessible so prospective and current students can explore the curriculum.
    Supports department filtering via ?dept= query parameter.
    """
    student = getattr(request.user, 'student_profile', None) if request.user.is_authenticated else None
    all_active_courses = Course.objects.filter(is_active=True)
    departments = all_active_courses.values_list('department', flat=True).distinct().order_by('department')

    selected_dept = request.GET.get('dept', '').strip()
    courses = all_active_courses
    if selected_dept and selected_dept.lower() != 'all':
        courses = courses.filter(department__iexact=selected_dept)

    enrolled_course_ids = set()
    if student:
        enrolled_course_ids = set(
            student.enrollments.filter(status='active').values_list('course_id', flat=True)
        )

    total_catalog_count = all_active_courses.count()
    total_credits_sum = sum(c.credits for c in all_active_courses)

    context = {
        'courses': courses,
        'departments': departments,
        'selected_dept': selected_dept,
        'total_catalog_count': total_catalog_count,
        'total_credits_sum': total_credits_sum,
        'enrolled_course_ids': enrolled_course_ids,
    }
    return render(request, 'academics/course_list.html', context)


def course_detail_view(request, course_id):
    """
    View syllabus details, instructor info, and attendance records for a specific course.
    Publicly accessible so syllabi can be reviewed before enrollment.
    """
    course = get_object_or_404(Course, id=course_id)
    student = getattr(request.user, 'student_profile', None) if request.user.is_authenticated else None
    
    enrollment = None
    attendance_records = None
    total_sessions = 0
    present_sessions = 0
    attendance_percentage = None
    has_records = False
    is_good_standing = None

    if student:
        enrollment = Enrollment.objects.filter(student=student, course=course).first()
        attendance_records = Attendance.objects.filter(student=student, course=course).order_by('-date')
        total_sessions = attendance_records.count()
        present_sessions = attendance_records.filter(status__in=['present', 'late']).count()
        if total_sessions > 0:
            attendance_percentage = round((present_sessions / total_sessions) * 100, 1)
            has_records = True
            is_good_standing = (attendance_percentage >= 75.0)

    context = {
        'course': course,
        'enrollment': enrollment,
        'attendance_records': attendance_records,
        'total_sessions': total_sessions,
        'present_sessions': present_sessions,
        'attendance_percentage': attendance_percentage,
        'has_records': has_records,
        'is_good_standing': is_good_standing,
    }
    return render(request, 'academics/course_detail.html', context)


@require_POST
@login_required
def course_enroll_view(request, course_id):
    """
    Enroll the logged-in student into a course.
    """
    student = getattr(request.user, 'student_profile', None)
    if not student:
        messages.error(request, "Student profile required to enroll in courses.")
        return redirect('dashboard:dashboard')

    course = get_object_or_404(Course, id=course_id, is_active=True)

    enrollment, created = Enrollment.objects.get_or_create(
        student=student,
        course=course,
        defaults={'status': 'active'}
    )

    if not created:
        if enrollment.status != 'active':
            enrollment.status = 'active'
            enrollment.save()
            messages.success(request, f"Re-enrolled in {course.code} - {course.name} successfully!")
        else:
            messages.info(request, f"You are already actively enrolled in {course.code}.")
    else:
        messages.success(request, f"Successfully enrolled in {course.code} - {course.name}!")

    return redirect('dashboard:dashboard')


@require_POST
@login_required
def course_drop_view(request, course_id):
    """
    Drop an actively enrolled course.
    """
    student = getattr(request.user, 'student_profile', None)
    if not student:
        messages.error(request, "Student profile required.")
        return redirect('dashboard:dashboard')

    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(student=student, course=course, status='active').first()

    if enrollment:
        enrollment.status = 'dropped'
        enrollment.save()
        messages.info(request, f"Dropped course {course.code} - {course.name}.")
    else:
        messages.warning(request, f"You are not actively enrolled in {course.code}.")

    return redirect('dashboard:dashboard')
