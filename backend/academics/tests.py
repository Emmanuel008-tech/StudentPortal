import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from accounts.models import Student
from academics.models import Course, Enrollment, Attendance


class AcademicsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='academicstudent',
            email='academic@campus.edu',
            password='Password123!'
        )
        self.student = Student.objects.create(
            user=self.user,
            roll_number='STU-ACAD-001',
            department='Computer Science'
        )
        self.course1 = Course.objects.create(
            code='CS101',
            name='Introduction to Programming',
            description='Core computer science concepts.',
            credits=4,
            instructor='Prof. Turing',
            department='Computer Science'
        )
        self.course2 = Course.objects.create(
            code='DS201',
            name='Data Science Essentials',
            description='Data analysis and statistics.',
            credits=3,
            instructor='Dr. Shannon',
            department='Data Science'
        )

    def test_course_creation_and_str(self):
        """Test Course model attributes and string representation."""
        self.assertEqual(str(self.course1), 'CS101 - Introduction to Programming')
        self.assertEqual(self.course1.credits, 4)

    def test_enrollment_unique_constraint(self):
        """Verify student cannot be enrolled in the same course twice."""
        Enrollment.objects.create(student=self.student, course=self.course1)
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(student=self.student, course=self.course1)

    def test_attendance_unique_constraint(self):
        """Verify duplicate attendance on the same date for same course is rejected."""
        today = datetime.date.today()
        Attendance.objects.create(student=self.student, course=self.course1, date=today, status='present')
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(student=self.student, course=self.course1, date=today, status='absent')

    def test_course_enroll_and_drop_views_post_only(self):
        """Test student enrolling in and dropping a course requires POST (GET rejected with 405)."""
        self.client.login(username='academicstudent', password='Password123!')

        enroll_url = reverse('academics:course_enroll', args=[self.course2.id])
        # GET should be rejected with 405 Method Not Allowed
        get_response = self.client.get(enroll_url)
        self.assertEqual(get_response.status_code, 405)
        self.assertFalse(
            Enrollment.objects.filter(student=self.student, course=self.course2, status='active').exists()
        )

        # POST should succeed and enroll the student
        post_response = self.client.post(enroll_url)
        self.assertRedirects(post_response, reverse('dashboard:dashboard'))
        self.assertTrue(
            Enrollment.objects.filter(student=self.student, course=self.course2, status='active').exists()
        )

        drop_url = reverse('academics:course_drop', args=[self.course2.id])
        # GET should be rejected with 405 Method Not Allowed
        get_drop_response = self.client.get(drop_url)
        self.assertEqual(get_drop_response.status_code, 405)
        self.assertEqual(Enrollment.objects.get(student=self.student, course=self.course2).status, 'active')

        # POST should succeed and mark enrollment as dropped
        post_drop_response = self.client.post(drop_url)
        self.assertRedirects(post_drop_response, reverse('dashboard:dashboard'))
        enrollment = Enrollment.objects.get(student=self.student, course=self.course2)
        self.assertEqual(enrollment.status, 'dropped')

    def test_course_list_department_filtering(self):
        """Test course list page filtering by department via ?dept= query parameter."""
        self.client.login(username='academicstudent', password='Password123!')
        url = reverse('academics:course_list')
        
        # Unfiltered list shows both courses
        response_all = self.client.get(url)
        self.assertEqual(response_all.status_code, 200)
        self.assertContains(response_all, 'CS101')
        self.assertContains(response_all, 'DS201')

        # Filter by Computer Science
        response_cs = self.client.get(url, {'dept': 'Computer Science'})
        self.assertEqual(response_cs.status_code, 200)
        self.assertContains(response_cs, 'CS101')
        self.assertNotContains(response_cs, 'DS201')

        # Filter by Data Science
        response_ds = self.client.get(url, {'dept': 'Data Science'})
        self.assertEqual(response_ds.status_code, 200)
        self.assertContains(response_ds, 'DS201')
        self.assertNotContains(response_ds, 'CS101')

    def test_public_course_catalog_and_enroll_redirect(self):
        """Guests can browse course catalog without login; clicking enroll points to login page."""
        # Anonymous GET to catalog
        catalog_url = reverse('academics:course_list')
        response = self.client.get(catalog_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'University Course Catalog')
        self.assertContains(response, 'CS101')
        self.assertContains(response, '/accounts/login/?next=/academics/courses/')

        # Anonymous GET to course detail
        detail_url = reverse('academics:course_detail', args=[self.course1.id])
        detail_res = self.client.get(detail_url)
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, 'Sign In to Enroll')
        self.assertContains(detail_res, f'/accounts/login/?next={detail_url}')
