from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

position_choices = (
    ("contributor", "Contributor"),
    ("reviewer", "Reviewer")
    )
    
department_choices = (
    ("computer engineering", "Computer Science"),
    ("information technology", "Information Technology"),
    ("civil engineering", "Civil Engineering"),
    ("electrical engineering", "Electrical Engineering"),
    ("mechanical engineering", "Mechanical Engineering"),
    ("chemical engineering", "Chemical Engineering"),
    ("aerospace engineering", "Aerospace Engineering"),
    ("biosciences and bioengineering", "Biosciences and  BioEngineering"),
    ("electronics", "Electronics"),
    ("energy science and engineering", "Energy Science and Engineering"),
    ("others", "Others")
    )

title = (
    ("Professor", "Prof."),
    ("Doctor", "Dr."),
    ("Shriman", "Shri"),
    ("Shrimati", "Smt"),
    ("Kumari", "Ku"),
    ("Mr", "Mr."),
    ("Mrs", "Mrs."),
    ("Miss", "Ms."),
    )

source = (
    ("FOSSEE website", "FOSSEE website"),
    ("Google", "Google"),
    ("Social Media", "Social Media"),
    ("From other College", "From other College"),
    ("others", "Others")
    )

states = (
    ("IN-AP",	"Andhra Pradesh"),
    ("IN-AR",	"Arunachal Pradesh"),
    ("IN-AS",	"Assam"),
    ("IN-BR",	"Bihar"),
    ("IN-CT",	"Chhattisgarh"),
    ("IN-GA",	"Goa"),
    ("IN-GJ",	"Gujarat"),
    ("IN-HR",	"Haryana"),
    ("IN-HP",	"Himachal Pradesh"),
    ("IN-JK",	"Jammu and Kashmir"),
    ("IN-JH",	"Jharkhand"),
    ("IN-KA",	"Karnataka"),
    ("IN-KL",	"Kerala"),
    ("IN-MP",	"Madhya Pradesh"),
    ("IN-MH",	"Maharashtra"),
    ("IN-MN",	"Manipur"),
    ("IN-ML",	"Meghalaya"),
    ("IN-MZ",	"Mizoram"),
    ("IN-NL",	"Nagaland"),
    ("IN-OR",	"Odisha"),
    ("IN-PB",	"Punjab"),
    ("IN-RJ",	"Rajasthan"),
    ("IN-SK",	"Sikkim"),
    ("IN-TN",	"Tamil Nadu"),
    ("IN-TG",	"Telangana"),
    ("IN-TR",	"Tripura"),
    ("IN-UT",	"Uttarakhand"),
    ("IN-UP",	"Uttar Pradesh"),
    ("IN-WB",	"West Bengal"),
    ("IN-AN",	"Andaman and Nicobar Islands"),
    ("IN-CH",	"Chandigarh"),
    ("IN-DN",	"Dadra and Nagar Haveli"),
    ("IN-DD",	"Daman and Diu"),
    ("IN-DL",	"Delhi"),
    ("IN-LD",	"Lakshadweep"),
    ("IN-PY",	"Puducherry")
    )

def has_profile(user):
    """ check if user has profile """
    return True if hasattr(user, 'profile') else False


class Profile(models.Model):
    """Profile for users(instructors and coordinators)"""

    user = models.OneToOneField(User)
    title = models.CharField(max_length=32,blank=True, choices=title)
    institute = models.CharField(max_length=150)
    department = models.CharField(max_length=150, choices=department_choices)
    phone_number = models.CharField(
                max_length=10,
                validators=[RegexValidator(
                                regex=r'^.{10}$', message=(
                                "Phone number must be entered \
                                in the format: '9999999999'.\
                                Up to 10 digits allowed.")
                            )]
                ,null=False)
    position = models.CharField(max_length=32, choices=position_choices,
                  default='contributor')
    how_did_you_hear_about_us = models.CharField(max_length=255, blank=True,choices=source)
    location = models.CharField(max_length=255,blank=True, help_text="Place/City")
    state = models.CharField(max_length=255, choices=states, default="IN-MH")
    is_email_verified = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=255, blank=True, null=True)
    key_expiry_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return u"id: {0}| {1} {2} | {3} ".format(
                                            self.user.id,
                                            self.user.first_name,
                                            self.user.last_name,
                                            self.user.email
                                            )
