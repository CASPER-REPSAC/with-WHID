from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from dataclasses import fields
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic.edit import FormView
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django import forms as DjangoForm
from django.utils import timezone
from django.forms.models import model_to_dict
from .forms import *
from .models import *
from django.http import QueryDict


class StudygroupsView(FormView):
    form_class = GroupSearchForm
    template_name = 'group-search.html'

    def form_valid(self, form):
        searchWord = form.cleaned_data['search_word']
        group_list = Studygroups.objects.filter(Q(groupname__icontains=searchWord)).distinct()

        context = {}
        context['form'] = form
        context['search_term'] = searchWord
        context['studygroups'] = group_list
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


def check(request, pk):
    if request.method == "POST":
        uid = int(request.session['_auth_user_id'])
        if uid != str(request.user.id):
            return render(request, 'error.html')
        # skey=request.session.session_key
        # sessions=Session.objects.get(session_key=skey)
        # s_data = sessions.get_decoded()
        else:
            input_passcode = request.POST.get('passcode')
            try:
                group = Studygroups.objects.filter(groupid=pk, grouppasscode=input_passcode)
                try:
                    test = group.get(grouppasscode=input_passcode)
                except:
                    return HttpResponse("입장 코드가 올바르지 않습니다.")
                context = {'groupss': group}
                user = AuthUser.objects.get(id=int(uid))
                groups = Studygroups.objects.get(groupid=pk)
                mapping = UsersGroupsMapping.objects.get_or_create(useridx=user, groupidx=groups)
                if (mapping[1] == True):
                    return render(request, 'join.html', context)
                else:
                    return HttpResponse("이미 가입된 그룹입니다.")
            except:
                return render(request, 'error.html')


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

        return render(self.request, self.template_name, context)


def join(request, pk):
    if request.method == "GET":
        studygroup = Studygroups.objects.filter(groupid=pk).distinct()
        context = {
            'studygroup': studygroup
        }
        return render(request, 'join.html', context)


# Default Page
def index(request):
    page = request.GET.get('page', 1)
    if dict(request.session):
        queryset_list = []
        if request.method == 'GET':
            user_id = int(request.session['_auth_user_id'])
            usr_grp_mapping = UsersGroupsMapping.objects.filter(useridx=user_id)
            for mapping_model in usr_grp_mapping:
                queryset_list += GroupAssignments.objects.filter(groupid=mapping_model.groupidx)
            return render(request, 'calendar.html', {"data": [x for x in map(model_to_dict, queryset_list)]})
    return render(request, 'calendar.html')


def error(request):
    return render(request, "error.html")


# Personal Feature
def socialauth(request, exception):
    return render(request, "socialauth.html")


def userinfo(request):
    # if request.method=="POST":
    uid = int(request.session['_auth_user_id'])
    model = UsersGroupsMapping.objects.filter(useridx=int(uid)).distinct()
    context = {}
    context['studygroups'] = model
    return render(request, "mypage.html", context)


def calendarDetail(request, date_time: str):
    # 우선 date_time 값를 url 로 'YYYY-MM-DD' 형식의 데이터를 입력받는다.
    date = date_time
    # calendar 처럼 user_id 가 4라고 가정하고,
    user_id = int(request.session['_auth_user_id'])
    queryset_list = []
    if request.method == 'GET':
        usr_grp_mapping = UsersGroupsMapping.objects.filter(useridx=user_id)
        for mapping_model in usr_grp_mapping:
            # 여기까진 calendar 랑 같음.
            queryset_list += GroupCalendar.objects \
                .filter(groupid=mapping_model.groupidx) \
                .filter(groupplanstart__lte=date + ' 23:59:59', groupplanend__gte=date + ' 00:00:00')
    context = {'queryset_list': queryset_list}
    return render(request, "calendar-detail.html", context=context)


# Group Feature
def getUserObject_or_404(user_id: int, group_id: int):
    user_object = get_object_or_404(AuthUser, pk=user_id)
    group_object = Studygroups.objects.get(pk=group_id)
    get_object_or_404(UsersGroupsMapping, useridx=user_object, groupidx=group_object)
    return user_object


#######################
# Article
def groupArticleCreate(request, group_id):
    user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    group = get_object_or_404(Studygroups, groupid=group_id)
    if request.method == "POST":
        category = int(request.POST['grouparticlecategory'][0])
        if user_id.pk != group.groupmaster.pk and category == 1:
            return redirect('whatshouldido:error')
        article_form = GroupArticlesForm(request.POST)
        if article_form.is_valid():
            article = article_form.save(commit=False)
            article.grouparticlecategory = category
            article.uploaddate = timezone.now()
            article.userid = user_id
            article.groupid = get_object_or_404(Studygroups, pk=group_id)
            article.save()
            return redirect('whatshouldido:group-article-read', group_id=group_id, article_id=article.pk)
    context = {'form': GroupArticlesForm(), 'group': group}
    return render(request, "group-article-write.html", context)


def groupArticleList(request, group_id):
    user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    article_data = GroupArticles.objects.filter(userid=user_id)
    article_data = [article_obj
                    for article_obj in map(model_to_dict,
                                           [article_obj for article_obj in article_data])]
    return render(request, 'group-article-list.html', {'article_data': article_data})


def groupArticleRead(request, group_id, article_id):
    user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    article = get_object_or_404(GroupArticles, id=article_id)
    #########CommentPART###########

    context = model_to_dict(article)
    context['groupname'] = article.groupid.groupname
    context['authorname'] = article.userid.username
    comments = GroupArticleComments.objects.all()
    return render(request, 'group-article-read.html',
                  {'article_data': context, "comments": comments,
                   'comment_form': GroupArticleCommentsForm()})


def commentCreate(request, group_id, article_id):
    user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    article = get_object_or_404(GroupArticles, id=article_id)
    if request.method == "POST":
        comment_form = GroupArticleCommentsForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.articleid = article
            comment.writer = user_id
            comment.writedate = timezone.now()
            comment.save()
            return redirect('whatshouldido:group-article-read', group_id=group_id, article_id=article_id)
    return redirect('whatshouldido:group-article-read', group_id=group_id, article_id=article_id)


def commentDelete(request, group_id, article_id):
    user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    article = get_object_or_404(GroupArticles, id=article_id)
    if request.method == "POST":
        comment = get_object_or_404(GroupArticleComments, pk=int(request.POST['commentid']))
        if user_id == comment.writer:
            comment.delete()
            return redirect('whatshouldido:group-article-read', group_id=group_id, article_id=article_id)
    return redirect('whatshouldido:group-article-read', group_id=group_id, article_id=article_id)


def groupArticleEdit(request, group_id, article_id):
    user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    group = get_object_or_404(Studygroups, groupid=group_id)
    article = get_object_or_404(GroupArticles, pk=article_id)
    if request.method == "POST":
        # 이 글이 현재 유저의 소유인지 확인
        if user_id == article.userid:
            return redirect('whatshouldido:group-article-list', group_id=group_id)
        category = int(request.POST['grouparticlecategory'][0])
        if user_id.pk != group.groupmaster.pk and category == 1:
            return redirect('whatshouldido:error')
        article_form = GroupArticlesForm(request.POST, instance=article)
        if article_form.is_valid():
            article = article_form.save(commit=False)
            article.grouparticlecategory = category
            article.uploaddate = timezone.now()
            article.userid = user_id
            article.groupid = get_object_or_404(Studygroups, pk=group_id)
            article.save()
            return redirect('whatshouldido:group-article-read', group_id=group_id, article_id=article.pk)
    context = {'form': GroupArticlesForm(instance=article), 'group': group, 'article': article}
    return render(request, "group-article-write.html", context)


def groupArticleDelete(request, group_id, article_id):
    user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    # 이 글이 현재 유저의 소유인지 확인
    article = get_object_or_404(GroupArticles, pk=article_id)
    if user_id == article.userid:
        article.delete()
        return redirect('whatshouldido:group-article-list', group_id=group_id)

    return redirect('whatshouldido:error')


#######################
# Assignment
def groupAssignmentList(request, group_id):
    getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    assign_data = GroupAssignments.objects.filter(groupid=group_id)
    assign_data = [assign_obj
                   for assign_obj in map(model_to_dict,
                                         [assign_obj for assign_obj in assign_data])]

    return render(request, 'group-assign-list.html', {'assign_data': assign_data})


def groupAssignmentCreate(request, group_id):
    user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    group = get_object_or_404(Studygroups, groupid=group_id)
    if user_id.pk != group.groupmaster.pk:
        return redirect('whatshouldido:error')
    if request.method == "POST":
        assign_form = GroupAssignmentsForm(request.POST)
        if assign_form.is_valid():
            assign = assign_form.save(commit=False)
            assign.groupid = get_object_or_404(Studygroups, pk=group_id)
            assign.save()
            return redirect('whatshouldido:group-assign-read', group_id=group_id, assign_id=assign.pk)
    context = {'form': GroupAssignmentsForm()}
    return render(request, "group-assign-write.html", context)


def groupAssignmentEdit(request, group_id, assign_id):
    # request 에서 pk 4번으로 testMan AuthUser instance 를 가져왔다고 해보자
    user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    group = get_object_or_404(Studygroups, groupid=group_id)
    if user_id.pk != group.groupmaster.pk:
        return redirect('whatshouldido:error')
    assign = get_object_or_404(GroupAssignments, id=assign_id)
    if request.method == "POST":
        assign_form = GroupAssignmentsForm(request.POST, instance=assign)
        if assign_form.is_valid():
            assign = assign_form.save(commit=False)
            assign.save()
            return redirect('whatshouldido:group-assign-read',
                            group_id=group_id, article_id=assign.pk)
    context = {'form': GroupAssignmentsForm(instance=assign)}
    return render(request, "group-assign-write.html", context)


def groupAssignmentRead(request, group_id, assign_id):
    getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    # 유저와 그룹이 맵핑 되어있는지 확인 아니면 404 뿜뿜
    assign_data = get_object_or_404(GroupAssignments, id=assign_id)
    context = model_to_dict(assign_data)

    return render(request, 'group-assign-read.html', {'assign_data': context})


def groupAssignmentDelete(request, group_id, assign_id):
    # 유저와 그룹이 맵핑 되어있는지 확인 아니면 404 뿜뿜
    user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
    group = get_object_or_404(Studygroups, groupid=group_id)
    if user_id.pk != group.groupmaster.pk:
        return redirect('whatshouldido:error')
    # 이 그룹이 현재 유저의 소유인지 확인
    group = get_object_or_404(Studygroups, groupid=group_id)
    if user_id.pk == group.groupmaster.id:
        get_object_or_404(GroupAssignments, id=assign_id).delete()
        return redirect('whatshouldido:group-assign-list', group_id=group_id)


#######################

def groupSearch(request):
    if request.method == 'GET':
        group_list = Studygroups.objects.order_by('groupname')
    else:
        group_list = None
    context = {'studygroups': group_list}
    return render(request, "group-search.html", context)


def groupCreate(request):
    # request 에서 pk 4번으로 testMan AuthUser instance 를 가져왔다고 해보자
    user_id = get_object_or_404(AuthUser, pk=int(request.session['_auth_user_id']))
    if request.method == "POST":
        group_form = StudygroupsForm(request.POST)
        if group_form.is_valid():
            group = group_form.save(commit=False)
            group.groupmaster = user_id
            group.save()
            group_mapping = UsersGroupsMapping(
                useridx=group.groupmaster,
                groupidx=group)
            group_mapping.save()
            return redirect('whatshouldido:groupinfo', group_id=group.pk)
    form = StudygroupsForm()
    return render(request, 'group-make.html', {'form': form})


def groupInfo(request, group_id):
    try:
        group_data = Studygroups.objects.get(groupid=group_id)
        context = model_to_dict(group_data)
    except:
        return redirect('whatshouldido:error')

    return render(request, 'group-info.html', {'group_data': context})


def groupManage(request, group_id):
    # request 에서 pk 4번으로 testMan AuthUser instance 를 가져왔다고 해보자

    user_id = getUserObject_or_404(user_id=int(request.session['_auth_user_id']), group_id=group_id)
    group = get_object_or_404(Studygroups, pk=group_id)
    if request.method == "POST":
        group_form = StudygroupsForm(request.POST, instance=group)
        if group_form.is_valid():
            group = group_form.save(commit=False)
            group.groupmaster = user_id
            group.save()
            return redirect('whatshouldido:groupinfo', group_id=group.pk)
    form = StudygroupsForm(instance=group)
    return render(request, 'group-manage.html', {'form': form})
