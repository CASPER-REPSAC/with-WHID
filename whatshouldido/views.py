from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.http import HttpResponse
# Create your views here.


#Default Page
def index(request):
    page = request.GET.get('page',1)
    return render(request, 'base.html')

def error(request):
    return HttpResponse("error")

#Personal Feature
def login(request):
    return render(request, "social.html")

def logout(request):
    return HttpResponse("logout")

def signup(request):
    return HttpResponse("signup")

def userinfo(request):
    return HttpResponse("userinfo")

#Main Page Feature
def main(request):
    return HttpResponse("main")

def calendardetail(request, date):
    return HttpResponse("calendarDetail")

def groupsearch(request, search):
    return HttpResponse("groupsearch")


#Group Feature
def writearticle(request, group):
    return HttpResponse("writearticle")

def makegroup(request):
    return HttpResponse("makegroup")

def managegroup(request, group):
    return HttpResponse("managegroup")

def groupinfo(request, group):
    return HttpResponse("groupinfo")