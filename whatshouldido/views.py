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
    if request.method == 'GET':
        user_id = 4
        usr_grp_mapping = models.UsersGroupsMapping.objects.filter(useridx=user_id)
        for mapping_model in usr_grp_mapping:
            queryset_list += models.GroupCalendar.objects.filter(groupid=mapping_model.groupidx)

    context = {'queryset_list': queryset_list}
    # for plan in queryset_list:
    #     print(plan, plan.groupplanid, plan.groupplanname, plan.groupplaninfo)
    return render(request, "calendar.html", context=context)


def signup(request):
    return HttpResponse("signup")


def userinfo(request):
    return HttpResponse("userinfo")


# Main Page Feature
def main(request):
    return HttpResponse("main")


def calendardetail(request, date):
    return HttpResponse("calendarDetail")


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
