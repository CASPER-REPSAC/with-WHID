from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'whatshouldido'

urlpatterns = [
    # Main Page
    path('', views.index, name='index'),
    path('auth/logout', LogoutView.as_view()),

    # Pop-up
    path('error', views.error, name='error'),

    path('search', views.groupSearch, name='groupsearch'),

    # Personal Page
    path('userinfo', views.userInfo, name='userinfo'),
    path('calendar', views.calendar, name='calendar'),
    path('calendardetail/<str:date_time>', views.calendarDetail, name='calendardetail'),

    # Group Feature Page
    path('group/<int:pk>/writearticle', views.writeArticle, name='writearticle'),
    path('group/<int:pk>', views.groupinfo, name='groupinfo'),
    path('test', views.manageGroup, name='managegroup'),  # How?
    path('group/make', views.makeGroup, name='makegroup'),
]
