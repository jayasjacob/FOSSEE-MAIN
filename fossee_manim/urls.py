from django.conf.urls import url
from fossee_manim import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.user_register, name='register'),
    url(r'^activate_user/(?P<key>.+)$', views.activate_user),
    url(r'^activate_user/$', views.activate_user),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^send_proposal/$', views.send_proposal, name='send_proposal'),
    url(r'^edit_proposal/([1-9][0-9]*)$', views.edit_proposal,
        name='edit_proposal'),
    url(r'^proposal_status/$', views.proposal_status, name='proposal_status'),
    url(r'^search/$', views.search, name='search'),
    url(r'^view_profile/$', views.view_profile, name='view_profile'),
    url(r'^edit_profile/$', views.edit_profile, name='edit_profile')
]