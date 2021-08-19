from django.urls import path
from . import views

app_name ='whatshouldido'

urlpatterns = [
    #Default Page
    path('',views.index,name='index'),
    path('',views.error,name='error'),

    #Personal Page
    path('',views.login,name='login'),
    path('',views.signup, name='signup'),
    path('',views.logout, name='logout'),
    path('',views.userinfo,name='userinfo'),

    #Main Page
    path('',views.main,name='main'),
    path('',views.calendardetail,name='calendardetail'),

    #Group Feature Page
    path('',views.writearticle, name='writearticle'),
    path('',views.groupinfo, name='groupinfo'),
    path('',views.makegroup,name='makegroup'),
    path('',views.managegroup,name='managegroup'),
]