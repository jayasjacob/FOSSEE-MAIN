from django.conf.urls import url
from fossee_manim import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.user_register),
    url(r'^activate_user/(?P<key>.+)$', views.activate_user),
    url(r'^activate_user/$', views.activate_user),
    url(r'^login/$', views.user_login),
    url(r'^logout/$', views.user_logout),
    url(r'^view_profile/$', views.view_profile),
    url(r'^edit_profile/$', views.edit_profile)
]