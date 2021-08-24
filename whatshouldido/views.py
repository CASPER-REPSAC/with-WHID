from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic.edit import FormView
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django import forms
from .forms import *
from .models import *


class StudygroupsView(FormView):
    form_class = GroupSearchForm
    template_name = 'group-search.html'
    def form_valid(self, form):
        print(form)
        searchWord = form.cleaned_data['search_word']
        print(searchWord)
        group_list = Studygroups.objects.filter(Q(groupname__icontains=searchWord)).distinct()

        context = {}
        context['form'] = form
        context['search_term'] = searchWord
        context['studygroups'] = group_list
        print(context)
        return render(self.request, self.template_name, context)

'''
def groupsearch(request,search_term):
    if request.method == 'GET':
        searchWord = search_term.cleaned_data['search_word']
        print(searchWord)
        group_list = Studygroups.objects.order_by('groupname')
        context = {'studygroups' : group_list }
    print(context)
    return render(request,"base.html",context)
'''
def check(request,pk):
    if request.method=="POST":
        input_passcode = request.POST.get('passcode')
        skey=request.session.session_key
        session=Session.objects.get(session_key=skey)
        s_data = session.get_decoded()
        uid = s_data.get('_auth_user_id')
        if(uid == str(request.user.id) ):
            #try:
            group = Studygroups.objects.filter(groupid=pk, grouppasscode=input_passcode)
            context={'groupss': group }
            user = AuthUser.objects.get(id=int(uid))
            print("USER")
            print(user)
            groups = Studygroups.objects.get(groupid=pk)
            print("Group")
            print(groups)
            mapping = UsersGroupsMapping.objects.get_or_create(useridx=user,groupidx=groups)
            if(mapping[1]==True):
                return render(request, 'join.html', context)
            else:
                return HttpResponse("이미 가입된 그룹입니다.")
            #except:
            #    print('4')
            #    return render(request, 'error.html')
        else:
            print('5')
            return render(request,'error.html')


class MappingView(FormView):
    form_class = UsersGroupsMappingForm
    template_name = 'join.html'
    def form_valid(self, form):
        searchWord = form.cleaned_data['search_word']
        group_list = Studygroups.objects.filter(Q(groupname__icontains=searchWord)).distinct()

        context = {}
        context['form'] = form
        context['search_term'] = searchWord
        context['studygroups'] = group_list
        print(context)
        return render(self.request, self.template_name, context)

def join(request, pk):
    if request.method=="GET":
        studygroup = Studygroups.objects.filter(groupid=pk).distinct()
        print(studygroup)
        context = {
            'studygroup' : studygroup
        }
        return render(request, 'join.html', context)

#Default Page
def index(request):
    page = request.GET.get('page',1)
    return render(request, 'calendar.html')

def error(request):
    return render(request, "error.html")

#Personal Feature
def socialauth(request, exception):
    return render(request, "socialauth.html")

def calendar(request):
    return render(request, "calendar.html")

def userinfo(request):
    return HttpResponse("userinfo")

#Main Page Feature
def main(request):
    return HttpResponse("main")

def calendardetail(request, date):
    return HttpResponse("calendarDetail")

#Group Feature
def writearticle(request, group):
    return HttpResponse("writearticle")

def makegroup(request):
    return HttpResponse("makegroup")

def managegroup(request, group):
    return HttpResponse("managegroup")

def groupinfo(request, group):
    return HttpResponse("groupinfo")