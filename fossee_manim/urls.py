from django.conf.urls import url
from fossee_manim import views
from django.conf import settings
from django.conf.urls.static import static


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
    url(r'^upload_animation/([1-9][0-9]*)$', views.upload_animation,
        name='upload_animation'),
    url(r'^proposal_status/$', views.proposal_status, name='proposal_status'),
    url(r'^search/$', views.search, name='search'),
    url(r'^guidelines/$', views.guidelines, name='guidelines'),
    url(r'^view_profile/$', views.view_profile, name='view_profile'),
    url(r'^edit_profile/$', views.edit_profile, name='edit_profile'),
    url(r'^video/([1-9][0-9]*)$', views.video, name='video'),
    url(r'^honorarium/$', views.honorarium, name='honorarium'),
    url(r'^faqs/$', views.faqs, name='faqs'),
    url(r'^search_category/(?P<cat>.+)$', views.search_category,
        name='search_category'),
    url(r'^about/$',views.about, name='about'),
    url(r'^explore/(?P<category>.+)$', views.explore,
        name='explore'),
]

urlpatterns += static(
                    settings.MEDIA_URL,
                    document_root=settings.MEDIA_ROOT
)
