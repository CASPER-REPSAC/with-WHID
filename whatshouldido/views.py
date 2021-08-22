from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic.edit import FormView
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