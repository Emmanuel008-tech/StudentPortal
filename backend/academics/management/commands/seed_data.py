import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from accounts.models import Student
from academics.models import Course, Enrollment, Attendance


class Command(BaseCommand):
    help = "Seeds database with demo students, courses, enrollments, and attendance records."

    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")

        admin_username = getattr(settings, 'ADMIN_BOOTSTRAP_USERNAME', 'admin')
        admin_password = getattr(settings, 'ADMIN_BOOTSTRAP_PASSWORD', 'adminpassword123')
        student_password = getattr(settings, 'STUDENT_BOOTSTRAP_PASSWORD', 'student123!')

        # 1. Admin Superuser
        admin_user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                'email': 'admin@campuspulse.edu',
                'first_name': 'Portal',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password(admin_password)
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_username} (password configured in .env)"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Synchronized existing admin user: {admin_username}"))

        # 2. Demo Student Users
        students_data = [
            {
                'username': 'alex_morgan',
                'first_name': 'Alex',
                'last_name': 'Morgan',
                'email': 'alex.morgan@campus.edu',
                'roll_number': 'STU-2026-0042',
                'department': 'Computer Science',
                'phone': '+1 (555) 019-2834',
                'bio': 'Junior Computer Science student passionate about distributed systems, UI design, and open source development.',
            },
            {
                'username': 'jordan_lee',
                'first_name': 'Jordan',
                'last_name': 'Lee',
                'email': 'jordan.lee@campus.edu',
                'roll_number': 'STU-2026-0089',
                'department': 'Data Science',
                'phone': '+1 (555) 014-9921',
                'bio': 'Data Science enthusiast researching predictive modeling and high-throughput data processing.',
            },
            {
                'username': 'priya_sharma',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'email': 'priya.sharma@campus.edu',
                'roll_number': 'STU-2026-0115',
                'department': 'Information Tech',
                'phone': '+1 (555) 018-7733',
                'bio': 'Cloud infrastructure apprentice and cybersecurity learner working towards certified security associate.',
            }
        ]

        created_students = {}
        for s_data in students_data:
            user, u_created = User.objects.get_or_create(
                username=s_data['username'],
                defaults={
                    'email': s_data['email'],
                    'first_name': s_data['first_name'],
                    'last_name': s_data['last_name'],
                }
            )
            if u_created:
                user.set_password(student_password)
                user.save()

            student, st_created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'roll_number': s_data['roll_number'],
                    'department': s_data['department'],
                    'phone': s_data['phone'],
                    'bio': s_data['bio'],
                }
            )
            created_students[s_data['username']] = student
            self.stdout.write(f"Processed student profile: {student.roll_number} ({user.username})")

        # 3. Courses
        courses_data = [
            {
                'code': 'CS101',
                'name': 'Principles of Computer Science & Algorithms',
                'description': 'Foundational computational thinking, algorithm complexity, memory architectures, and core programming paradigms in Python.',
                'credits': 4,
                'instructor': 'Prof. Alan Turing',
                'department': 'Computer Science',
            },
            {
                'code': 'CS205',
                'name': 'Data Structures & Algorithmic Analysis',
                'description': 'In-depth study of stacks, queues, balanced search trees, graph traversals, and dynamic programming with real-world benchmarks.',
                'credits': 4,
                'instructor': 'Dr. Ada Lovelace',
                'department': 'Computer Science',
            },
            {
                'code': 'WEB301',
                'name': 'Full-Stack Modern Web Architectures',
                'description': 'Client-server communications, semantic HTML5 design systems, vanilla JavaScript, relational databases, and secure Django integration.',
                'credits': 3,
                'instructor': 'Prof. Grace Hopper',
                'department': 'Web Engineering',
            },
            {
                'code': 'DS204',
                'name': 'Applied Machine Learning & Statistical Inference',
                'description': 'Supervised and unsupervised learning, regression models, cross-validation methods, and exploratory data pipelines.',
                'credits': 4,
                'instructor': 'Dr. Andrew Ng',
                'department': 'Data Science',
            },
            {
                'code': 'UIUX110',
                'name': 'Human-Centered Interaction & Design Systems',
                'description': 'Cognitive psychology of interfaces, typographic hierarchy, color contrast accessibility (WCAG AA), and user testing protocols.',
                'credits': 3,
                'instructor': 'Prof. Don Norman',
                'department': 'Design',
            },
            {
                'code': 'CYBER220',
                'name': 'Network Security & Defensive Cryptography',
                'description': 'Symmetric & asymmetric cipher suites, authentication tokens, network packet analysis, and mitigation of common web vulnerabilities.',
                'credits': 3,
                'instructor': 'Dr. Bruce Schneier',
                'department': 'Cybersecurity',
            },
        ]

        created_courses = {}
        for c_data in courses_data:
            course, created = Course.objects.get_or_create(
                code=c_data['code'],
                defaults=c_data
            )
            if not created:
                for k, v in c_data.items():
                    setattr(course, k, v)
                course.save()
            created_courses[c_data['code']] = course
            self.stdout.write(f"Course ready: {course.code} - {course.name} ({course.department})")

        # 4. Enrollments for Alex Morgan
        alex = created_students['alex_morgan']
        alex_course_codes = ['CS101', 'CS205', 'WEB301', 'UIUX110']
        
        for code in alex_course_codes:
            Enrollment.objects.get_or_create(
                student=alex,
                course=created_courses[code],
                defaults={'status': 'active'}
            )

        # Enrollments for Jordan and Priya
        Enrollment.objects.get_or_create(student=created_students['jordan_lee'], course=created_courses['DS204'])
        Enrollment.objects.get_or_create(student=created_students['jordan_lee'], course=created_courses['CS205'])
        Enrollment.objects.get_or_create(student=created_students['priya_sharma'], course=created_courses['WEB301'])
        Enrollment.objects.get_or_create(student=created_students['priya_sharma'], course=created_courses['CYBER220'])

        # 5. Attendance Records for Alex Morgan
        # Generate realistic date sequence over recent 25 weekdays
        today = datetime.date.today()
        weekdays = []
        cur = today - datetime.timedelta(days=45)
        while len(weekdays) < 20 and cur <= today:
            if cur.weekday() < 5:  # Monday to Friday
                weekdays.append(cur)
            cur += datetime.timedelta(days=1)

        # CS101: 18 sessions, 16 present, 1 late, 1 absent (~94% -> Teal)
        cs101_course = created_courses['CS101']
        for i, date_val in enumerate(weekdays[:18]):
            status = 'present'
            if i == 5:
                status = 'late'
            elif i == 11:
                status = 'absent'
            Attendance.objects.get_or_create(
                student=alex,
                course=cs101_course,
                date=date_val,
                defaults={'status': status}
            )

        # CS205: 16 sessions, 14 present, 2 absent (~87.5% -> Teal)
        cs205_course = created_courses['CS205']
        for i, date_val in enumerate(weekdays[:16]):
            status = 'absent' if i in (3, 9) else 'present'
            Attendance.objects.get_or_create(
                student=alex,
                course=cs205_course,
                date=date_val,
                defaults={'status': status}
            )

        # WEB301: 15 sessions, 10 present, 5 absent (~66.7% -> Coral Alert Badge!)
        web301_course = created_courses['WEB301']
        for i, date_val in enumerate(weekdays[:15]):
            status = 'absent' if i in (1, 4, 7, 10, 13) else 'present'
            Attendance.objects.get_or_create(
                student=alex,
                course=web301_course,
                date=date_val,
                defaults={'status': status}
            )

        # UIUX110: 12 sessions, 11 present, 1 late (~100% -> Teal)
        uiux110_course = created_courses['UIUX110']
        for i, date_val in enumerate(weekdays[:12]):
            status = 'late' if i == 6 else 'present'
            Attendance.objects.get_or_create(
                student=alex,
                course=uiux110_course,
                date=date_val,
                defaults={'status': status}
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded student portal with courses and realistic attendance records!"))
