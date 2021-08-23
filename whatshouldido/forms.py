from django import forms
from django.forms import widgets
from whatshouldido.models import AuthUser, Studygroups, UsersGroupsMapping, GroupArticles, GroupAssignments, \
    GroupCalendar


class AuthUserForm(forms.ModelForm):
    class Meta:
        model = AuthUser
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'date_joined']
        labels = {
            'username': '아이디',
            'password': '비밀번호',
            'first_name': '이름',
            'last_name': '성',
            'email': '이메일',
            'date_joined': '가입일',
        }


class StudygroupsForm(forms.ModelForm):
    # 그룹 만들 때, 그룹장은 입력받을 필요 없어서 뺐습니다.
    class Meta:
        model = Studygroups
        fields = ['groupname', 'grouppasscode', ]  # 'groupmaster']
        labels = {
            'groupname': '스터디 그룹 명',
            'grouppasscode': '스터디 그룹 입장 코드',
            # 'groupmaster': '그룹장',
        }


class UsersGroupsMappingForm(forms.ModelForm):
    class Meta:
        model = UsersGroupsMapping
        fields = ['useridx', 'groupidx']
        labels = {
            'useridx': '그룹 멤버',
            'groupidx': '소속 그룹',
        }


class GroupArticlesForm(forms.ModelForm):
    class Meta:
        model = GroupArticles
        fields = ['userid', 'grouparticletitle', 'grouparticlecontent', 'grouparticlecategory', 'uploaddate']
        labels = {
            'userid': '작성자',
            'grouparticletitle': '게시글 제목',
            'grouparticlecontent': '게시글 내용',
            'grouparticlecategory': '게시글 카테고리',
            'uploaddate': '게시일자',
        }


class GroupAssignmentsForm(forms.ModelForm):
    class Meta:
        model = GroupAssignments
        fields = ['groupassignment', 'groupassignmentdetail', 'groupassignmentlimit']
        labels = {
            'groupassignment': '과제',
            'groupassignmentdetail': '과제 정보',
            'groupassignmentlimit': '과제 기한',
        }


class GroupCalendarForm(forms.ModelForm):
    class Meta:
        model = GroupCalendar
        fields = ['groupplanname', 'groupplaninfo', 'groupplanlink', 'groupplanstart', 'groupplanend']
        labels = {
            'groupplanname': '일정 명',
            'groupplaninfo': '일정 정보',
            'groupplanlink': '접속 정보',
            'groupplanstart': '일정 시작 시간',
            'groupplanend': '일정 종료 시간',
        }
