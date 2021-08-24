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
    path('calendardetail/<str:date_time>', views.calendarDetail, name='calendar-detail'),

    # Group Feature Page
    path('group/<int:group_id>/article/create', views.groupArticleCreate, name='group-article-create'),
    path('group/<int:group_id>/article/<int:article_id>', views.groupArticleRead, name='group-article-read'),
    path('group/<int:group_id>/article/<int:article_id>/edit', views.groupArticleEdit, name='group-article-edit'),

    path('group/<int:group_id>/assign/create', views.groupAssignmentCreate, name='group-assignment-create'),
    path('group/<int:group_id>/assign/<int:assign_id>', views.groupAssignmentRead, name='group-assignment-read'),
    path('group/<int:group_id>/assign/<int:assign_id>/edit', views.groupAssignmentEdit, name='group-assignment-edit'),


    path('group/make', views.groupMake, name='groupmake'),
    path('group/<int:group_id>', views.groupInfo, name='groupinfo'),
    path('group/<int:group_id>/manage', views.groupManage, name='groupmanage'),  # 이렇게. <-- How?
]







