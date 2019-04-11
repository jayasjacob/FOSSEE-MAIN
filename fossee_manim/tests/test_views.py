from django.test import TestCase
from fossee_manim.models import (
                    Profile, User, Category, Animation,
					Comment, AnimationStats, has_profile
                    )
from datetime import datetime
from django.test import Client
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from fossee_manim.views import view_profile, user_login, edit_profile

class TestProfile(TestCase):
	def setUp(self):
		self.client = Client()

		self.user1 = User.objects.create(
			username='demo_test_user1',
			password='pass@123',
			email='test.user@gmail.com')

		self.user2 = User.objects.create(
			username='demo_test_user2',
			email='test.user@gmail.com')

		self.user2.set_password('pass@123')
		self.user2.save()

		self.user2_profile = Profile.objects.create(
			user=self.user2,
			department='Computer Engineering',
			institute='ace',
			title='Doctor',
			position='instructor',
			phone_number='1122993388',
			location='mumbai',
			how_did_you_hear_about_us='Google',
			state='IN-MH',
			is_email_verified=1
			)

	def test_has_profile_for_user_without_profile(self):
		"""
		If no profile exists for user passed as argument return False
		"""
		has_profile_status = has_profile(self.user1)
		self.assertFalse(has_profile_status)

	def test_has_profile_for_user_with_profile(self):
		"""
		If profile exists for user passed as argument return True
		"""
		has_profile_status = has_profile(self.user2)
		self.assertTrue(has_profile_status)

	def test_view_profile_denies_anonymous(self):
		"""
		If not logged in redirect to login page
		"""
		response = self.client.get(reverse(view_profile), follow=True)
		redirect_destination = '/login/?next=/view_profile/'
		self.assertTrue(response.status_code,200)
		self.assertRedirects(response, redirect_destination)

	def test_edit_profile_get(self):
		"""
		GET request to edit profile should display profile form
		"""

		self.client.login(username=self.user2, password='pass@123')
		response = self.client.get(reverse(edit_profile))
		user_profile = User.objects.get(id=self.user2.id)
		profile = Profile.objects.get(user=user_profile)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(profile.institute, 'ace')
		self.client.logout()

	def test_edit_profile_post(self):

		self.client.login(username=self.user2, password='pass@123')
		response = self.client.post('/edit_profile/',
			{
				'first_name': 'demo_test',
				'last_name': 'user2',
				'institute': 'IIT',
				'department': 'aerospace engineering'
					})
	
		updated_profile_user = User.objects.get(id=self.user2.id)
		updated_profile = Profile.objects.get(user=updated_profile_user)
		self.assertEqual(updated_profile.institute, 'IIT')
		self.assertEqual(updated_profile.department, 'aerospace engineering')
		self.assertEqual(updated_profile.position, 'instructor')
		self.assertEqual(response.status_code, 200)
