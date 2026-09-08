from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import Student
from academics.models import Course, Attendance


def landing_view(request):
    """
    Homepage with course-centered hero mosaic, left-aligned layout rhythm,
    feature highlights teaser, and asymmetrical course spotlight.
    """
    all_courses = list(Course.objects.filter(is_active=True))
    mosaic_courses = all_courses[:4] if len(all_courses) >= 4 else all_courses
    spotlight_course = next((c for c in all_courses if c.code == 'WEB301'), all_courses[0] if all_courses else None)
    secondary_courses = [c for c in all_courses if spotlight_course and c.id != spotlight_course.id][:2]
    
    total_students = Student.objects.count()
    total_courses = len(all_courses)
    total_attendance_logs = Attendance.objects.count()

    return render(request, 'landing.html', {
        'all_courses': all_courses,
        'mosaic_courses': mosaic_courses,
        'spotlight_course': spotlight_course,
        'secondary_courses': secondary_courses,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_attendance_logs': total_attendance_logs,
    })


def about_view(request):
    """
    Full dedicated About page detailing the portal's mission,
    the 75% attendance policy, faculty governance, and campus values.
    """
    total_students = Student.objects.count()
    total_courses = Course.objects.filter(is_active=True).count()
    return render(request, 'about.html', {
        'total_students': total_students,
        'total_courses': total_courses,
    })


def features_view(request):
    """
    Full dedicated Features page showcasing all functional capabilities
    of CampusPulse with detailed descriptions and visual tags.
    """
    return render(request, 'features.html')


def contact_view(request):
    """
    Full dedicated Contact page with an interactive inquiry form,
    registrar office hours, physical campus location, and support directory.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        if not name or not email or not message_text:
            messages.error(request, "Please fill in all required fields (Name, Email, and Message).")
            return render(request, 'contact.html', {
                'submitted_name': name,
                'submitted_email': email,
                'submitted_subject': subject,
                'submitted_message': message_text,
            })

        # In development/demo, simulate message receipt and log/flash confirmation
        messages.success(
            request,
            f"Thank you, {name}! Your message regarding '{subject or 'General Inquiry'}' has been received. "
            f"The Academic Advising & Registrar team will respond to {email} within 1 business day."
        )
        return redirect('contact')

    return render(request, 'contact.html')

