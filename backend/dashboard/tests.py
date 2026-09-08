import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Student
from academics.models import Course, Enrollment, Attendance


class DashboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='dashstudent',
            email='dash@campus.edu',
            password='Password123!',
            first_name='Dash',
            last_name='Student'
        )
        self.student = Student.objects.create(
            user=self.user,
            roll_number='STU-DASH-001',
            department='Computer Science'
        )
        self.course_good = Course.objects.create(
            code='CS101',
            name='Algorithms 101',
            description='Algorithmic foundations.',
            credits=4,
            instructor='Prof. Lovelace'
        )
        self.course_alert = Course.objects.create(
            code='WEB301',
            name='Web Engineering',
            description='Web architectures.',
            credits=3,
            instructor='Dr. Berners-Lee'
        )

        Enrollment.objects.create(student=self.student, course=self.course_good, status='active')
        Enrollment.objects.create(student=self.student, course=self.course_alert, status='active')

        # Add 4 sessions for course_good: 3 present, 1 absent -> 75.0% (Good Standing)
        base_date = datetime.date.today() - datetime.timedelta(days=10)
        Attendance.objects.create(student=self.student, course=self.course_good, date=base_date, status='present')
        Attendance.objects.create(student=self.student, course=self.course_good, date=base_date + datetime.timedelta(days=1), status='present')
        Attendance.objects.create(student=self.student, course=self.course_good, date=base_date + datetime.timedelta(days=2), status='present')
        Attendance.objects.create(student=self.student, course=self.course_good, date=base_date + datetime.timedelta(days=3), status='absent')

        # Add 4 sessions for course_alert: 2 present, 2 absent -> 50.0% (Alert < 75%)
        Attendance.objects.create(student=self.student, course=self.course_alert, date=base_date, status='present')
        Attendance.objects.create(student=self.student, course=self.course_alert, date=base_date + datetime.timedelta(days=1), status='present')
        Attendance.objects.create(student=self.student, course=self.course_alert, date=base_date + datetime.timedelta(days=2), status='absent')
        Attendance.objects.create(student=self.student, course=self.course_alert, date=base_date + datetime.timedelta(days=3), status='absent')

    def test_dashboard_login_required(self):
        """Unauthenticated user should be redirected to login."""
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_view_renders_student_data(self):
        """Logged-in student should see profile, enrolled courses, and calculated attendance badges."""
        self.client.login(username='dashstudent', password='Password123!')
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)

        # Profile verification
        self.assertContains(response, 'Dash Student')
        self.assertContains(response, 'STU-DASH-001')

        # Course chips verification
        self.assertContains(response, 'CS101')
        self.assertContains(response, 'WEB301')

        # Attendance badge calculation verification
        # 75.0% for CS101 -> good standing badge
        self.assertContains(response, '75.0% Present')
        # 50.0% for WEB301 -> alert badge
        self.assertContains(response, '50.0% Alert')

    def test_dashboard_zero_attendance_sessions_shows_neutral_badge(self):
        """Course with zero attendance sessions displays neutral badge instead of 100% Good Standing."""
        course_zero = Course.objects.create(
            code='HIST101',
            name='World History',
            description='Global historical developments.',
            credits=3,
            instructor='Prof. Wells'
        )
        Enrollment.objects.create(student=self.student, course=course_zero, status='active')

        self.client.login(username='dashstudent', password='Password123!')
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)

        # Must display neutral badge
        self.assertContains(response, 'No sessions yet')
        self.assertContains(response, 'badge-neutral')

        # Must not claim 100% for HIST101
        self.assertNotContains(response, '100.0% Present')
        self.assertNotContains(response, '100% Present')

        # Course detail should also display neutral status
        detail_response = self.client.get(reverse('academics:course_detail', args=[course_zero.id]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'No sessions yet')
        self.assertContains(detail_response, 'No lecture or lab sessions recorded yet')

