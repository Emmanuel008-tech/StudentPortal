from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from academics.models import Course, Attendance
from accounts.models import Student


class StudentPortalPublicPagesTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='portaltestuser',
            email='portaltest@campus.edu',
            password='TestPassword123!'
        )
        self.student = Student.objects.create(
            user=self.user,
            roll_number='STU-PORTAL-01',
            department='Computer Science'
        )
        self.course = Course.objects.create(
            code='CS101',
            name='Principles of Computer Science',
            description='Foundational algorithms and data concepts.',
            credits=4,
            instructor='Prof. Ada Lovelace',
            department='Computer Science',
            is_active=True
        )

    def test_landing_page_renders_hero_and_live_stats(self):
        """Landing page renders the course-centered hero with mosaic and feature teasers."""
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Every course, every credit, one clear view.")
        self.assertContains(response, "hero-banner-courses")
        self.assertContains(response, "course-mosaic")
        self.assertContains(response, "Browse Courses")
        self.assertContains(response, "Staff Login")

    def test_about_page_renders(self):
        """About page renders institutional mission and 75% attendance standard."""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About CampusPulse")
        self.assertContains(response, "The 75% Attendance Policy")
        self.assertContains(response, "Our Educational Mission")

    def test_features_page_renders(self):
        """Features page renders comprehensive capability pillars."""
        response = self.client.get(reverse('features'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Platform Capabilities &amp; Features")
        self.assertContains(response, "Attendance Intelligence")
        self.assertContains(response, "Self-Service Course Management")
        self.assertContains(response, "Verified Student Identity")

    def test_contact_page_get_and_post(self):
        """Contact page displays inquiry form and processes valid submissions with feedback."""
        # GET request
        get_response = self.client.get(reverse('contact'))
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, "Contact Academic Services")
        self.assertContains(get_response, "Send an Academic Inquiry")

        # Incomplete POST
        invalid_post = self.client.post(reverse('contact'), {
            'name': '',
            'email': 'student@campus.edu',
            'subject': 'Attendance Dispute',
            'message': ''
        })
        self.assertEqual(invalid_post.status_code, 200)
        self.assertContains(invalid_post, "Please fill in all required fields")

        # Valid POST
        valid_post = self.client.post(reverse('contact'), {
            'name': 'Alex Morgan',
            'email': 'alex.morgan@campus.edu',
            'subject': 'Attendance Dispute',
            'message': 'Discrepancy with CS101 session on Sept 1st.'
        })
        self.assertRedirects(valid_post, reverse('contact'))

    def test_staff_login_url_resolution(self):
        """Verify staff_login reverses cleanly and both /accounts/staff-login/ and /staff-login/ are reachable."""
        self.assertEqual(reverse('staff_login'), '/accounts/staff-login/')
        
        response1 = self.client.get(reverse('staff_login'))
        self.assertEqual(response1.status_code, 200)
        self.assertContains(response1, "Faculty &amp; Staff Login")

        response2 = self.client.get('/staff-login/')
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, "Faculty &amp; Staff Login")

    def test_django_admin_login(self):
        """Verify Django's /admin/ remains reachable and authenticates superuser."""
        superuser = User.objects.create_superuser(
            username='adminsuper',
            email='admin@campus.edu',
            password='AdminPassword123!'
        )
        response = self.client.post('/admin/login/', {
            'username': 'adminsuper',
            'password': 'AdminPassword123!',
        })
        # Successful auth in Django admin redirects to admin index or dashboard
        self.assertEqual(response.status_code, 302)
