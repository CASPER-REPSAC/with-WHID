from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


#Default Page
def index(request):
    return HttpResponse("StartPage")

def error(request):
    return HttpResponse("error")

#Personal Feature
def login(request):
    return HttpResponse("login")

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


#Group Feature
def writearticle(request, group):
    return HttpResponse("writearticle")

def makegroup(request):
    return HttpResponse("makegroup")

def managegroup(request, group):
    return HttpResponse("managegroup")

def groupinfo(request, group):
    return HttpResponse("groupinfo")