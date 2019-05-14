from django.test import TestCase
from fossee_manim.models import (
                    Profile, User, Category, Animation,
					Comment, AnimationStats
                    )
from datetime import datetime

# Setup for Model Test
def setUpModule():
	'''
		Sets up database 
		demo user as contributor and test user as reviewer
	'''

	demoUser1 = User.objects.create(username='demouser1', 
						email='test.user@gmail.com', password='pass@123')
	demoUser2 = User.objects.create(username='demouser2', 
						email='test.user@gmail.com', password='pass@123')

	testUser1 = User.objects.create(username='testuser1',
						email='test.user@gmail.com',password='pass@123')

	testUser2 = User.objects.create(username='testuser2',
				email='test.user@gmail.com', password='pass@123')

	category1 = Category.objects.create(name='Math', description='Mathematics')

	reviewer_profile = Profile.objects.create(user=testUser2, position='reviewer',
			department='computer science', institute='ace', phone_number='1122334456', 
			title='Doctor', how_did_you_hear_about_us='Google', location='powai', state='IN-MH',
			is_email_verified=1)

	contributor_profile = Profile.objects.create(user=demoUser2, position='contributor',
			department='IT', institute='iit', phone_number='1122334456',location='powai',
			title='Doctor', how_did_you_hear_about_us='Google', state='IN-MH',
			is_email_verified=1)



def tearDownModule():
	User.objects.all().delete()
	Profile.objects.all().delete()
	Category.objects.all().delete()


class ProfileModelTest(TestCase):
	'''	
		This class tests the Profile Model
	'''
	def setUp(self):
		'''
			setsup profile for reviewer and contributor
		'''	
		self.testuser1 = User.objects.get(username='testuser1')
		self.demouser1 = User.objects.get(username='demouser1')
		
		self.reviewer_profile1 = Profile.objects.create(user=self.testuser1, 
								position='reviewer', department='computer science', 
								institute='ace', phone_number='1123323344',
								title='Doctor', how_did_you_hear_about_us='Google', location='powai', state='IN-MH',
								is_email_verified=1)

		self.contributor_profile1 = Profile.objects.create(user=self.demouser1, position='contributor',
								department='IT', institute='iit', phone_number='1122334455',
								title='Doctor', how_did_you_hear_about_us='Google', location='powai', state='IN-MH',
								is_email_verified=1)

	def test_profile_model(self):
		self.assertEqual(self.demouser1.email,'test.user@gmail.com')
		self.assertEqual(self.testuser1.email,'test.user@gmail.com')
		self.assertEqual(self.reviewer_profile1.position,'reviewer')
		self.assertEqual(self.contributor_profile1.position,'contributor')
		self.assertEqual(self.contributor_profile1.location,'powai')
		self.assertEqual(self.reviewer_profile1.location,'powai')
		self.assertEqual(self.contributor_profile1.how_did_you_hear_about_us,'Google')


class CategoryModelTest(TestCase):
	def setUp(self):
		self.category1 = Category.objects.create(name='Biology', description='study of nature')
		self.category2 = Category.objects.create(name='Aerospace',
						description='Aerospace is the human effort in science, engineering, and business to fly in the atmosphere of Earth \
						(aeronautics) and surrounding space (astronautics). \
						Aerospace organizations research, design, manufacture, operate, or maintain aircraft or spacecraft. Aerospace activity \
						is very diverse, with a multitude of commercial, industrial and military applications.'
						)
	
	def test_category_model(self):
		self.assertEqual(self.category1.description, 'study of nature')
		self.assertEqual(self.category2.name, 'Aerospace')
	

class AnimationModelTest(TestCase):
	def setUp(self):
		self.demoUser2 = User.objects.create(username='demouser21', 
						email='test.user@gmail.com', password='pass@123')
		self.testUser2 = User.objects.create(username='testuser21',
				email='test.user@gmail.com', password='pass@123')
		self.category1 = Category.objects.create(name='Biology', description='study of nature')
		self.animation1 = Animation.objects.create(title='Testing Anime', contributor=self.demoUser2,
		reviewer=self.testUser2, outline='This is test animation upload',
		category=self.category1)

	def test_animation_model(self):
		self.assertEqual(self.animation1.title, 'Testing Anime')
		self.assertEqual(self.category1.name, 'Biology')


class CommentModelTest(TestCase):
	def setUp(self):
		self.demoUser2 = User.objects.create(username='demouser21', 
						email='test.user@gmail.com', password='pass@123')
		self.testUser2 = User.objects.create(username='testuser21',
				email='test.user@gmail.com', password='pass@123')
		self.category1 = Category.objects.create(name='Biology', description='study of nature')
		self.animation1 = Animation.objects.create(title='Testing Anime', contributor=self.demoUser2,
		reviewer=self.testUser2, outline='This is test animation upload',
		category=self.category1)
		self.comment1 = Comment.objects.create(comment='This is a comment', commentor=self.testUser2,
		animation=self.animation1, animation_status='changes')

	def test_comment_model(self):
		self.assertEqual(self.comment1.comment, 'This is a comment')
