from dataclasses import fields

from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.core.paginator import Paginator
from whatshouldido import forms, models
from django.utils import timezone
from django.forms.models import model_to_dict


# Create your views here.


# Default Page
def index(request):
    page = request.GET.get('page', 1)
    return render(request, 'base.html')


def error(request):
    return render(request, "error.html")


# Personal Feature
def socialAuth(request, exception):
    return render(request, "socialauth.html")


def calendar(request):
    # 현재 유저의 id를 어떻게 가져옴?
    # >>> 소셜 로그인이 되면 auth_user, socialaccount 둘다 insert 되므로
    # >>> socialaccount 테이블에서 uid 값을 통해 user_id 를 불러오자

    # 보안상 쿠키 체크를 해야할 것 같음.
    # 일단 testMan 으로 진행
    # 1. 가입된 그룹의 id 들을 가져옴
    # 1-1. 가입된 그룹이 없을 경우 => 빈 리스트 반환
    # 2. 가져온 그룹의 id를 이용하여, group_calendar 에서 오브젝트를 가져옴
    # 2-1. 등록된 오브젝트가 없을 경우 => 빈 리스트 반환
    # 3. 가져온 오브젝트들을 묶어서 context 로 반환.
    # 4. 전체적으로 오류가 있을 경우, 일단 빈 리스트를 반환 or error 로 redirect
    # 별도의 인증 절차를 거친 후 testMan(id = 4) 가 접근했다고 하자
    queryset_list = []
    user_id = 4
    # uid = request.META.get('HTTP_USER_ID')
    # user_id = models.SocialaccountSocialaccount.objects.filter(uid=uid)
    if request.method == 'GET':
        usr_grp_mapping = models.UsersGroupsMapping.objects.filter(useridx=user_id)
        for mapping_model in usr_grp_mapping:
            queryset_list += models.GroupCalendar.objects.filter(groupid=mapping_model.groupidx)

    context = {'queryset_list': queryset_list}
    return render(request, "calendar.html", context=context)


def calendarDetail(request, date_time: str):
    # (str) Sun Aug 22 2021 13:01:30 GMT+0900 종환이 형이 알려준  datetime 포맷
    # 우선 date_time 값를 url 로 'YYYY-MM-DD' 형식의 데이터를 입력받는다.
    date = date_time
    # calendar 처럼 user_id 가 4라고 가정하고,
    user_id = 4
    queryset_list = []
    if request.method == 'GET':
        usr_grp_mapping = models.UsersGroupsMapping.objects.filter(useridx=user_id)
        for mapping_model in usr_grp_mapping:
            # 여기까진 calendar 랑 같음.
            queryset_list += models.GroupCalendar.objects \
                .filter(groupid=mapping_model.groupidx) \
                .filter(groupplanstart__lte=date + ' 23:59:59', groupplanend__gte=date + ' 00:00:00')
            # 다른 점은 추가된 새로운 필터인데, 조건 키워드라는게 따로 있더라,
            # __lte => less than or equal
            # __gte => greater than or equal
            # 이하, 이상의 의미이니, e 를 빼면, 각각 미만, 초과가 된다.
            # 자세한 것은 https://brownbears.tistory.com/63 에 Filter 에 조건 키워드 참고
            # 22일 부터 시작인 프로젝트는 22일로 검색이 안된다 23일로하면 된다...
            # 아무래도 시간의 영향 같다.
            # 그래서 날짜를 입력받으면 뒤에 시간 23:59:59, 00:00:00 을 붙여서
            # 하루짜리 스터디도 조회할 수 있도록 하였다.
        print(queryset_list)
    context = {'queryset_list': queryset_list}
    return render(request, "calendar-detail.html", context=context)


def signUp(request):
    return HttpResponse("signup")


def userInfo(request):
    return HttpResponse("userinfo")


def main(request):
    return HttpResponse("main")


# Main Page Feature\

# Group Feature
def getUserObject_or_404(user_id: int, group_id: int):
    user_object = get_object_or_404(models.AuthUser, pk=user_id)
    group_object = models.Studygroups.objects.get(pk=group_id)
    get_object_or_404(models.UsersGroupsMapping, useridx=user_object, groupidx=group_object)
    return user_object


def groupArticleCreate(request, group_id):
    # request 에서 pk 4번으로 testMan AuthUser instance 를 가져왔다고 해보자
    user_id = getUserObject_or_404(4, group_id)
    if request.method == "POST":
        article_form = forms.GroupArticlesForm(request.POST)
        if article_form.is_valid():
            article = article_form.save(commit=False)
            article.uploaddate = timezone.now()
            article.userid = user_id
            article.groupid = get_object_or_404(models.Studygroups, pk=group_id)
            article.save()
            return redirect('whatshouldido:group-article-read', group_id=group_id, article_id=article.pk)
    context = {'form': forms.GroupArticlesForm()}
    return render(request, "group-article-write.html", context)


def groupArticleEdit(request, group_id, article_id):
    # request 에서 pk 4번으로 testMan AuthUser instance 를 가져왔다고 해보자
    user_id = getUserObject_or_404(4, group_id)
    article = get_object_or_404(models.GroupArticles, id=article_id)
    if request.method == "POST":
        article_form = forms.GroupArticlesForm(request.POST, instance=article)
        if article_form.is_valid():
            article = article_form.save(commit=False)
            # article.uploaddate = timezone.now() # 수정할 때 게시된 시간은 바뀌면 안되겠지
            article.save()
            return redirect('whatshouldido:group-article-read', group_id=group_id, article_id=article.pk)
    context = {'form': forms.GroupArticlesForm(instance=article)}
    return render(request, "group-article-write.html", context)


def groupArticleRead(request, group_id, article_id):
    getUserObject_or_404(4, group_id)
    # 유저와 그룹이 맵핑 되어있는지 확인 아니면 404 뿜뿜
    article_data = get_object_or_404(models.GroupArticles, id=article_id)
    context = model_to_dict(article_data)
    context['groupname'] = article_data.groupid.groupname
    context['authorname'] = article_data.userid.username

    return render(request, 'group-article-read.html', {'article_data': context})


def groupAssignmentCreate(request, group_id):
    # request 에서 pk 4번으로 testMan AuthUser instance 를 가져왔다고 해보자
    user_id = getUserObject_or_404(4, group_id)
    if request.method == "POST":
        assign_form = forms.GroupAssignmentsForm(request.POST)

        if assign_form.is_valid():
            assign = assign_form.save(commit=False)
            assign.uploaddate = timezone.now()
            assign.userid = user_id
            assign.groupid = get_object_or_404(models.Studygroups, pk=group_id)
            assign.save()
            return redirect('whatshouldido:group-assignment-read', group_id=group_id, article_id=assign.pk)

    context = {'form': forms.GroupAssignmentsForm()}
    return render(request, "group-assgin-create.html", context)


def groupAssignmentEdit(request, group_id, article_id):
    # request 에서 pk 4번으로 testMan AuthUser instance 를 가져왔다고 해보자
    user_id = getUserObject_or_404(4, group_id)
    article = get_object_or_404(models.GroupArticles, id=article_id)
    if request.method == "POST":
        article_form = forms.GroupArticlesForm(request.POST, instance=article)
        if article_form.is_valid():
            article = article_form.save(commit=False)
            # article.uploaddate = timezone.now() # 수정할 때 게시된 시간은 바뀌면 안되겠지
            article.save()
            return redirect('whatshouldido:group-assignment-read', group_id=group_id, article_id=article.pk)
    context = {'form': forms.GroupArticlesForm(instance=article)}
    return render(request, "group-article-write.html", context)


def groupAssignmentRead(request, group_id, article_id):
    getUserObject_or_404(4, group_id)
    # 유저와 그룹이 맵핑 되어있는지 확인 아니면 404 뿜뿜
    article_data = get_object_or_404(models.GroupArticles, id=article_id)
    context = model_to_dict(article_data)
    context['groupname'] = article_data.groupid.groupname
    context['authorname'] = article_data.userid.username

    return render(request, 'group-article-read.html', {'article_data': context})


def groupSearch(request):
    if request.method == 'GET':
        group_list = models.Studygroups.objects.order_by('groupname')
    else:
        group_list = None
    context = {'studygroups': group_list}
    return render(request, "group-search.html", context)


def groupMake(request):
    # request 에서 pk 4번으로 testMan AuthUser instance 를 가져왔다고 해보자
    user_id = models.AuthUser.objects.get(pk=4)
    if request.method == "POST":
        group_form = forms.StudygroupsForm(request.POST)
        if group_form.is_valid():
            group = group_form.save(commit=False)
            group.groupmaster = user_id
            group.save()
            group_mapping = models.UsersGroupsMapping(
                useridx=group.groupmaster,
                groupidx=group)
            group_mapping.save()
            return redirect('whatshouldido:groupinfo', pk=group.pk)
    form = forms.StudygroupsForm()
    return render(request, 'group-make.html', {'form': form})


def groupManage(request, group):
    # request 에서 pk 4번으로 testMan AuthUser instance 를 가져왔다고 해보자
    user_id = models.AuthUser.objects.get(pk=4)
    group = get_object_or_404(models.Studygroups, pk=group)
    if request.method == "POST":
        group_form = forms.StudygroupsForm(request.POST, instance=group)
        if group_form.is_valid():
            group = group_form.save(commit=False)
            group.groupmaster = user_id
            group.save()
            return redirect('whatshouldido:groupinfo', pk=group.pk)
    form = forms.StudygroupsForm(instance=group)
    return render(request, 'group-manage.html', {'form': form})


def groupInfo(request, group):
    try:
        group_data = models.Studygroups.objects.get(groupid=group)
        context = [group_data.groupname, group_data.groupmaster]
    except:
        return redirect('whatshouldido:error')

    return render(request, 'group-info.html', {'group_data': context})
