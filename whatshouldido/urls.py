from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views
app_name = 'whatshouldido'

urlpatterns = [
    # Main Page
    path('', views.index, name='index'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('search', views.StudygroupsView.as_view(), name='groupsearch'),
    path('search/', views.StudygroupsView.as_view(), name='groupsearch'),
    path('search/<int:pk>', views.join, name='join'),
    path('check/<int:pk>', views.check, name='check'),

    # Pop-up
    path('error/', views.error, name='error'),

    # Personal Page
    path('userinfo/', views.userinfo, name='userinfo'),
    # path('calendar/', views.calendar, name='calendar'),
    path('calendardetail/<str:date_time>', views.calendarDetail, name='calendar-detail'),

    # Group Feature Page
    path('group/<int:group_id>/article', views.groupArticleList, name='group-article-list'),
    path('group/<int:group_id>/article/create', views.groupArticleCreate, name='group-article-create'),
    path('group/<int:group_id>/article/<int:article_id>', views.groupArticleRead, name='group-article-read'),
    path('group/<int:group_id>/article/<int:article_id>/edit', views.groupArticleEdit, name='group-article-edit'),
    path('group/<int:group_id>/article/<int:article_id>/delete', views.groupArticleDelete, name='group-article-delete'),

    path('group/<int:group_id>/assign', views.groupAssignmentList, name='group-assign-list'),
    path('group/<int:group_id>/assign/create', views.groupAssignmentCreate, name='group-assign-create'),
    path('group/<int:group_id>/assign/<int:assign_id>', views.groupAssignmentRead, name='group-assign-read'),
    path('group/<int:group_id>/assign/<int:assign_id>/edit', views.groupAssignmentEdit, name='group-assign-edit'),
    path('group/<int:group_id>/assign/<int:assign_id>/delete', views.groupAssignmentDelete, name='group-assign-delete'),

    path('group/create', views.groupCreate, name='groupcreate'),
    path('group/<int:group_id>', views.groupInfo, name='groupinfo'),
    path('group/<int:group_id>/manage', views.groupManage, name='groupmanage'),  # 이렇게. <-- How?
    path('group/<int:group_id>/manage/create', views.createGroupPlan, name='creategroupplan'),

    path('group/<int:group_id>/article/<int:article_id>/comment/create', views.commentCreate, name='comment-create'),
    path('group/<int:group_id>/article/<int:article_id>/comment/delete', views.commentDelete, name='comment-delete'),

    path('group/<int:group_id>/article/<int:article_id>/<int:file_id>', views.download_line, name="download")
]





