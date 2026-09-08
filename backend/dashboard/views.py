from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Student
from academics.models import Course, Enrollment, Attendance


@login_required
def dashboard_view(request):
    """
    Main student portal dashboard.
    Aggregates student profile, active course enrollments, attendance percentages,
    recent activity, and available courses to enroll.
    """
    user = request.user
    student = getattr(user, 'student_profile', None)

    if not student:
        # Create student profile on the fly if missing (e.g. for superusers)
        student = Student.objects.create(
            user=user,
            roll_number=f"ADM-{user.id:04d}" if user.is_staff else f"STU-{user.id:04d}",
            department="Computer Science"
        )

    # Active enrollments
    active_enrollments = (
        Enrollment.objects.filter(student=student, status='active')
        .select_related('course')
        .order_by('course__code')
    )

    # Calculate statistics & attendance breakdown per course
    courses_data = []
    total_attended_all = 0
    total_sessions_all = 0
    total_credits = 0

    for enrollment in active_enrollments:
        course = enrollment.course
        total_credits += course.credits
        
        # Course attendance records
        records = Attendance.objects.filter(student=student, course=course)
        total_sessions = records.count()
        present_count = records.filter(status='present').count()
        late_count = records.filter(status='late').count()
        absent_count = records.filter(status='absent').count()

        # Late counts as half or present; prompt says present/absent/late, we can consider present+late as attended
        attended_count = present_count + late_count

        # Calculate attendance percentage only when sessions exist
        if total_sessions > 0:
            percentage = round((attended_count / total_sessions) * 100, 1)
            has_records = True
            is_good_standing = (percentage >= 75.0)
        else:
            percentage = None
            has_records = False
            is_good_standing = None

        total_sessions_all += total_sessions
        total_attended_all += attended_count

        courses_data.append({
            'enrollment': enrollment,
            'course': course,
            'total_sessions': total_sessions,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'attended_count': attended_count,
            'percentage': percentage,
            'has_records': has_records,
            'is_good_standing': is_good_standing,
        })

    # Overall attendance percentage
    if total_sessions_all > 0:
        overall_attendance_pct = round((total_attended_all / total_sessions_all) * 100, 1)
        has_overall_records = True
        is_overall_good = (overall_attendance_pct >= 75.0)
    else:
        overall_attendance_pct = None
        has_overall_records = False
        is_overall_good = None

    # Recent attendance log (last 8 entries)
    recent_attendance = (
        Attendance.objects.filter(student=student)
        .select_related('course')
        .order_by('-date')[:8]
    )

    # Courses available to enroll in (not currently active for this student)
    enrolled_course_ids = [e.course.id for e in active_enrollments]
    available_courses = Course.objects.filter(is_active=True).exclude(id__in=enrolled_course_ids)[:6]

    context = {
        'student': student,
        'courses_data': courses_data,
        'enrolled_count': len(courses_data),
        'total_credits': total_credits,
        'overall_attendance_pct': overall_attendance_pct,
        'has_overall_records': has_overall_records,
        'is_overall_good': is_overall_good,
        'recent_attendance': recent_attendance,
        'available_courses': available_courses,
    }

    return render(request, 'dashboard/dashboard.html', context)
