from django.contrib import admin
import csv
from django.http import HttpResponse
from .models import (
				Profile
				)
# Register your models here.
try:
    from StringIO import StringIO as string_io
except ImportError:
    from io import BytesIO as string_io

#Custom Classes 
class ProfileAdmin(admin.ModelAdmin):
	list_display = ['title','user', 'institute','location','department',
					'phone_number','position']
	list_filter = ['position', 'department']
	actions = ['download_csv']

	def download_csv(self, request, queryset):
		openfile = string_io()
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment;\
										filename=profile_data.csv'

		writer = csv.writer(response)
		writer.writerow(['email_id', 'title','username', 'first_name', 'last_name', 
						'institute', 'location', 'department',
						'phone_number', 'position'])

		for q in queryset:
			writer.writerow([q.user.email, q.title, q.user, q.user.first_name,
							q.user.last_name, q.institute,
							q.location, q.department, q.phone_number,
							q.position])

		openfile.seek(0)
		response.write(openfile.read())
		return response

	download_csv.short_description = "Download CSV file for selected stats."




admin.site.register(Profile, ProfileAdmin)
