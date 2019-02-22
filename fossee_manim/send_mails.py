__author__ = "Akshen Doke"

import hashlib
import logging.config
import re
from django.core.mail import send_mail
from textwrap import dedent
from random import randint
from smtplib import SMTP
from django.utils.crypto import get_random_string
from string import punctuation, digits
try:
	from string import letters
except ImportError:
	from string import ascii_letters as letters
from fossee_anime.settings import (
					EMAIL_HOST,
					EMAIL_PORT,
					EMAIL_HOST_USER,
					EMAIL_HOST_PASSWORD,
					EMAIL_USE_TLS,
					PRODUCTION_URL,
					SENDER_EMAIL,
					ADMIN_EMAIL
					)
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from os import listdir, path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from time import sleep


def validateEmail(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",
					email) != None:
			return 1
		return 0


def generate_activation_key(username):
	"""Generates hashed secret key for email activation"""
	chars = letters + digits + punctuation
	secret_key = get_random_string(randint(10,40), chars)
	return hashlib.sha256((secret_key + username).encode('utf-8')).hexdigest()



def send_email(request, call_on,
			user_name=None, other_email=None,
			institute=None, key=None
			):
	'''
	'''
	try:
		with open(path.join(settings.LOG_FOLDER, 'emailconfig.yaml'), 'r') as configfile:
			config_dict = yaml.load(configfile)
		logging.config.dictConfig(config_dict)
	except:
		print('File Not Found and Configuration Error')

	if call_on == "Registration":
		message = dedent("""\
					Thank you for registering as a contributor with us.
					Please click on the below link to
					activate your account
					{0}/activate_user/{1}
					After activation you can proceed to submit proposals for
					animations.
					In case of queries regarding submition of proposal(s),
					revert to this email.""".format(PRODUCTION_URL, key))

		logging.info("New Registration from: %s", request.user.email)
		try:
			send_mail(
				"User/Contributor Registration at FOSSEE, IIT Bombay", message, SENDER_EMAIL,
				[request.user.email], fail_silently=True
				)

		except Exception:
			send_smtp_email(request=request,
				subject="User/Contributor Registration - FOSSEE, IIT Bombay",
				message=message, other_email=request.user.email,
				)