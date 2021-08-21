from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.core.paginator import Paginator
from . import forms, models

# Create your views here.


#Default Page
def index(request):
    page = request.GET.get('page',1)
    return render(request, 'base.html')

def error(request):
    return render(request, "error.html")

#Personal Feature
def socialauth(request, exception):
    return render(request, "socialauth.html")

def signup(request):
    return HttpResponse("signup")

def userinfo(request):
    return HttpResponse("userinfo")

#Main Page Feature
def main(request):
    return HttpResponse("main")

def calendardetail(request, date):
    return HttpResponse("calendarDetail")

def groupsearch(request):
    if request.method == 'GET':
        group_list = models.Studygroups.objects.order_by('groupname')
        context = {'studygroups' : group_list }
    print(context)
    return render(request,"group-search.html",context)


#Group Feature
def writearticle(request, group):
    return HttpResponse("writearticle")

def makegroup(request):
    return HttpResponse("makegroup")

def managegroup(request, group):
    return HttpResponse("managegroup")

def groupinfo(request, group):
    return HttpResponse("groupinfo")