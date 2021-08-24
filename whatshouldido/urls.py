from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'whatshouldido'

urlpatterns = [
    #Main Page
    path('',views.index,name='index'),
    path('auth/logout/', LogoutView.as_view(),name='logout'),
    path('search',views.StudygroupsView.as_view(),name='groupsearch'),
    path('search/',views.StudygroupsView.as_view(),name='groupsearch'),
    path('search/<int:pk>',views.join,name='join'),
    path('check/<int:pk>',views.check ,name='check'),

    #Pop-up
    path('error/',views.error,name='error'),

    #Personal Page
    path('userinfo/',views.userinfo,name='userinfo'),
    path('calendar/',views.calendar,name='calendar'),
    path('calendardetail/<str:date_time>', views.calendarDetail, name='calendar-detail'),

    # Group Feature Page
    path('group/<int:group_id>/article/create', views.groupArticleCreate, name='group-article-create'),
    path('group/<int:group_id>/article/<int:article_id>', views.groupArticleRead, name='group-article-read'),
    path('group/<int:group_id>/article/<int:article_id>/edit', views.groupArticleEdit, name='group-article-edit'),

    path('group/<int:group_id>/assign/create', views.groupAssignmentCreate, name='group-article-create'),
    path('group/<int:group_id>/assign/<int:assign_id>', views.groupAssignmentRead, name='group-article-read'),
    path('group/<int:group_id>/assign/<int:assign_id>/edit', views.groupAssignmentEdit, name='group-article-edit'),

    path('group/make', views.groupMake, name='groupmake'),
    path('group/<int:group_id>', views.groupInfo, name='groupinfo'),
    path('group/<int:group_id>/manage', views.groupManage, name='groupmanage'),  # 이렇게. <-- How?
]