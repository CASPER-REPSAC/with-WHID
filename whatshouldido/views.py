from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.core.paginator import Paginator
from whatshouldido import forms, models


# Create your views here.


# Default Page
def index(request):
    page = request.GET.get('page', 1)
    return render(request, 'base.html')


def error(request):
    return render(request, "error.html")


# Personal Feature
def socialauth(request, exception):
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
                .filter(groupplanstart__gte=date, groupplanend__lte=date)
            # 다른 점은 추가된 새로운 필터인데, 조건 키워드라는게 따로 있더라,
            # __lte => less than or equal
            # __gte => greater than or equal
            # 이하, 이상의 의미이니, e 를 빼면, 각각 미만, 초과가 된다.
            # 자세한 것은 https://brownbears.tistory.com/63 에 Filter 에 조건 키워드 참고
            # 블로그에 __lte, __gte 에 대한 설명이 반대로 되어있으니 주의
    context = {'queryset_list': queryset_list}
    return render(request, "calendar-detail.html", context=context)


def signup(request):
    return HttpResponse("signup")


def userinfo(request):
    return HttpResponse("userinfo")


def main(request):
    return HttpResponse("main")


# Main Page Feature


def groupsearch(request):
    if request.method == 'GET':
        group_list = models.Studygroups.objects.order_by('groupname')
        context = {'studygroups': group_list}
    print(context)
    return render(request, "group-search.html", context)


# Group Feature
def writearticle(request, group):
    return HttpResponse("writearticle")


def makegroup(request):
    return HttpResponse("makegroup")


def managegroup(request, group):
    return HttpResponse("managegroup")


def groupinfo(request, group):
    return HttpResponse("groupinfo")
