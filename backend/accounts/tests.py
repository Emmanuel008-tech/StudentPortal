from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Student


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='teststudent',
            email='teststudent@campus.edu',
            password='Password123!',
            first_name='Test',
            last_name='Student'
        )
        self.student = Student.objects.create(
            user=self.user,
            roll_number='STU-TEST-001',
            department='Computer Science',
            phone='+1 555-010-0001',
            bio='Computer Science test student'
        )

    def test_student_profile_creation(self):
        """Verify Student model creation and helper properties."""
        self.assertEqual(self.student.user.username, 'teststudent')
        self.assertEqual(self.student.roll_number, 'STU-TEST-001')
        self.assertEqual(self.student.full_name, 'Test Student')
        self.assertEqual(self.student.initials, 'TS')
        self.assertIn('STU-TEST-001', str(self.student))

    def test_registration_view_success(self):
        """Verify successful student registration flow."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newstudent',
            'email': 'newstudent@campus.edu',
            'first_name': 'New',
            'last_name': 'Student',
            'roll_number': 'STU-NEW-002',
            'department': 'Data Science',
            'phone': '+1 555-010-0002',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
        })
        self.assertRedirects(response, reverse('dashboard:dashboard'))
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        self.assertTrue(Student.objects.filter(roll_number='STU-NEW-002').exists())

    def test_registration_password_mismatch(self):
        """Verify registration fails when passwords don't match."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'mismatchuser',
            'email': 'mismatch@campus.edu',
            'first_name': 'Mis',
            'last_name': 'Match',
            'roll_number': 'STU-MIS-003',
            'department': 'Computer Science',
            'password': 'SecurePassword123!',
            'confirm_password': 'DifferentPassword456!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'confirm_password', "Passwords do not match. Please verify.")
        self.assertFalse(User.objects.filter(username='mismatchuser').exists())

    def test_login_view_valid_credentials(self):
        """Verify login succeeds with valid credentials."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'teststudent',
            'password': 'Password123!',
        })
        self.assertRedirects(response, reverse('dashboard:dashboard'))

    def test_login_view_invalid_credentials(self):
        """Verify login fails with wrong password."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'teststudent',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username/email or password")

    def test_logout_view(self):
        """Verify logout redirects to landing page."""
        self.client.login(username='teststudent', password='Password123!')
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('landing'))

    def test_staff_login_view_staff_success(self):
        """Staff user can successfully log into the staff portal."""
        staff_user = User.objects.create_user(
            username='professorturing',
            email='turing@campus.edu',
            password='StaffPassword123!',
            is_staff=True
        )
        response = self.client.post(reverse('accounts:staff_login'), {
            'username': 'professorturing',
            'password': 'StaffPassword123!',
        })
        self.assertRedirects(response, reverse('accounts:staff_dashboard'))

    def test_staff_login_view_student_rejected(self):
        """Student user is rejected from the staff portal with an access denied message."""
        response = self.client.post(reverse('accounts:staff_login'), {
            'username': 'teststudent',
            'password': 'Password123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Access denied. This portal is strictly for academic faculty and administrative staff.")

    def test_staff_dashboard_access_control(self):
        """Staff dashboard requires is_staff privilege."""
        # Anonymous user gets redirected
        anon_response = self.client.get(reverse('accounts:staff_dashboard'))
        self.assertRedirects(anon_response, reverse('accounts:staff_login'))

        # Student user gets redirected
        self.client.login(username='teststudent', password='Password123!')
        student_response = self.client.get(reverse('accounts:staff_dashboard'))
        self.assertRedirects(student_response, reverse('accounts:staff_login'))

        # Staff user gets 200 OK
        staff_user = User.objects.create_user(
            username='adminstaff',
            email='staff@campus.edu',
            password='StaffPassword123!',
            is_staff=True
        )
        self.client.login(username='adminstaff', password='StaffPassword123!')
        staff_response = self.client.get(reverse('accounts:staff_dashboard'))
        self.assertEqual(staff_response.status_code, 200)
        self.assertContains(staff_response, "Faculty & Staff Console")

    def test_password_reset_flow(self):
        """Verify requesting password reset sends email and redirects to done view."""
        from django.core import mail
        response = self.client.post(reverse('accounts:password_reset'), {
            'email': 'teststudent@campus.edu'
        })
        self.assertRedirects(response, reverse('accounts:password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("CampusPulse Password Reset Request", mail.outbox[0].subject)
        self.assertIn("Test Student", mail.outbox[0].body)
        self.assertIn("password-reset-confirm", mail.outbox[0].body)

        # Done page renders 200
        done_response = self.client.get(reverse('accounts:password_reset_done'))
        self.assertEqual(done_response.status_code, 200)
        self.assertContains(done_response, "Instructions Dispatched")

