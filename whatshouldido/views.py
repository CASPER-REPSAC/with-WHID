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
import hashlib, logging

def check_auth_user_id_exist(request):
    if '_auth_user_id' in dict(request.session):
        return True
    return False

log = logging.getLogger('django')

def check_auth_user_id_exist(request):
    if '_auth_user_id' in dict(request.session):
        return True
    return False

class StudygroupsView(FormView):
    form_class = GroupSearchForm
    template_name = 'group-search.html'

    def form_valid(self, form):
        try:
            searchWord = form.cleaned_data['search_word']
            group_list = Studygroups.objects.filter(Q(groupname__icontains=searchWord)).distinct()

            context = {'form': form, 'search_term': searchWord, 'studygroups': group_list}
            return render(self.request, self.template_name, context)
        except:
            return redirect('whatshouldido:error')


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
    try:
        if check_auth_user_id_exist:
            if request.method == "POST":
                uid = int(request.session['_auth_user_id'])
                if uid != int(request.user.id):
                    return render(request, 'error.html')
                # skey=request.session.session_key
                # sessions=Session.objects.get(session_key=skey)
                # s_data = sessions.get_decoded()
                else:
                    input_passcode = hashlib.sha256(str(request.POST.get('passcode')).encode()).hexdigest()
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
                        if not mapping[1]:
                            return HttpResponse("이미 가입된 그룹입니다.")
                        else:
                            return render(request, 'join.html', context)
                    except:
                        return render(request, 'error.html')
        return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')

''' old check
def check(request,pk):
    if request.method=="POST":
        uid = request.session['_auth_user_id']
        #skey=request.session.session_key
        #sessions=Session.objects.get(session_key=skey)
        #s_data = sessions.get_decoded()
        if(uid == str(request.user.id) ):

            input_passcode = request.POST.get('passcode')
            try:
                group = Studygroups.objects.filter(groupid=pk, grouppasscode=input_passcode)
                try:
                    test=group.get(grouppasscode=input_passcode)
                    print(test.grouppasscode)
                except:
                    log.warning(" Group Passcode invalid |Input : " + str(input_passcode) +"  User " + str(uid) )
                    return HttpResponse("입장 코드가 올바르지 않습니다.")
                context={'groupss': group }
                user = AuthUser.objects.get(id=int(uid))
                groups = Studygroups.objects.get(groupid=pk)
                mapping = UsersGroupsMapping.objects.get_or_create(useridx=user,groupidx=groups)
                if(mapping[1]==True):
                    return render(request, 'join.html', context)
                else:
                    log.warning(" Duplicated_Group_Join_Try | During User " + str(uid) + " ==>> Group " + str(pk))
                    return HttpResponse("이미 가입된 그룹입니다.")
            except:
                log.error(" Group Information Tampered | During User " + str(uid) + " ==>> Group " + str(pk))
                return render(request, 'error.html')
        else:
            log.error(" User Information Tampered | During User " + str(uid) + " ==>> Group " + str(pk))
            return render(request,'error.html')
'''


class MappingView(FormView):
    form_class = UsersGroupsMappingForm
    template_name = 'join.html'

    def form_valid(self, form):
        try:
            searchWord = form.cleaned_data['search_word']
            group_list = Studygroups.objects.filter(Q(groupname__icontains=searchWord)).distinct()
            context = {'form': form, 'search_term': searchWord, 'studygroups': group_list}
            return render(self.request, self.template_name, context)
        except:
            return redirect('whatshouldido:error')


def join(request, pk):
    try:
        if request.method == "GET":
            studygroup = Studygroups.objects.filter(groupid=pk).distinct()
            context = {
                'studygroup': studygroup
            }
            return render(request, 'join.html', context)
    except:
        return redirect('whatshouldido:error')


# Default Page
def index(request):
    try:
        page = request.GET.get('page', 1)
        if check_auth_user_id_exist(request):
            assign_list = []
            article_list = []
            if request.method == 'GET':
                user_id = int(request.session['_auth_user_id'])
                usr_grp_mapping = UsersGroupsMapping.objects.filter(useridx=user_id)
                for mapping_model in usr_grp_mapping:
                    assign_list += GroupAssignments.objects.filter(groupid=mapping_model.groupidx).order_by(
                        'groupassignmentlimit')

                for mapping_model in usr_grp_mapping:
                    article_list += GroupArticles.objects.filter(groupid=mapping_model.groupidx).order_by('-uploaddate')

                context = {"data": {'assign': [x for x in map(model_to_dict, assign_list)],
                                    'article': [x for x in map(model_to_dict, article_list)]}}
                return render(request, 'calendar.html', context)
        return render(request, 'calendar.html')
    except:
        return redirect('whatshouldido:error')


def error(request):
    return render(request, "error.html")


# Personal Feature


def socialauth(request, exception):
    return render(request, "socialauth.html")


def userinfo(request):
    if check_auth_user_id_exist(request):
        # if request.method=="POST":
        uid = int(request.session['_auth_user_id'])
        model = UsersGroupsMapping.objects.filter(useridx=int(uid)).distinct()
        context = {}
        context['studygroups'] = model
        return render(request, "mypage.html", context)
    else:
        return redirect('whatshouldido:index')


def calendarDetail(request, date_time: str):
    try:
        if check_auth_user_id_exist(request):
            # 우선 date_time 값를 url 로 'YYYY-MM-DD' 형식의 데이터를 입력받는다.
            date = date_time
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
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


# Group Feature
def getUserObject_or_404(user_id: int, group_id: int):
    user_object = get_object_or_404(AuthUser, pk=user_id)
    group_object = Studygroups.objects.get(pk=group_id)
    get_object_or_404(UsersGroupsMapping, useridx=user_object, groupidx=group_object)
    return user_object


#######################
# Group - Article
def groupArticleCreate(request, group_id):
    try:
        if check_auth_user_id_exist(request):
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
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def groupArticleList(request, group_id):
    try:
        if check_auth_user_id_exist(request):
            user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
            article_data = GroupArticles.objects.filter(groupid=group_id)
            article_data = [article_obj
                            for article_obj in map(model_to_dict,
                                                   [article_obj for article_obj in article_data])]
            return render(request, 'group-article-list.html', {'article_data': article_data})
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def groupArticleRead(request, group_id, article_id):
    try:
        if check_auth_user_id_exist(request):
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
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def commentCreate(request, group_id, article_id):
    try:
        if check_auth_user_id_exist(request):
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
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def commentDelete(request, group_id, article_id):
    try:
        if check_auth_user_id_exist(request):
            user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
            article = get_object_or_404(GroupArticles, id=article_id)
            if request.method == "POST":
                comment = get_object_or_404(GroupArticleComments, pk=int(request.POST['commentid']))
                if user_id == comment.writer:
                    comment.delete()
                    return redirect('whatshouldido:group-article-read', group_id=group_id, article_id=article_id)
            return redirect('whatshouldido:group-article-read', group_id=group_id, article_id=article_id)
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def groupArticleEdit(request, group_id, article_id):
    try:
        if check_auth_user_id_exist(request):
            user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
            group = get_object_or_404(Studygroups, groupid=group_id)
            article = get_object_or_404(GroupArticles, pk=article_id)
            if request.method == "POST":
                # 이 글이 현재 유저의 소유인지 확인
                if user_id.id != article.userid.id:
                    return redirect('whatshouldido:group-article-list', group_id=group_id)
                category = int(request.POST['grouparticlecategory'][0])
                print(category)
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
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def groupArticleDelete(request, group_id, article_id):
    try:
        if check_auth_user_id_exist(request):
            user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
            # 이 글이 현재 유저의 소유인지 확인
            article = get_object_or_404(GroupArticles, pk=article_id)
            if user_id == article.userid:
                article.delete()
                return redirect('whatshouldido:group-article-list', group_id=group_id)

            return redirect('whatshouldido:error')
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


#######################
# Group - Assignment
def groupAssignmentList(request, group_id):
    try:
        if check_auth_user_id_exist(request):
            getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
            assign_data = GroupAssignments.objects.filter(groupid=group_id)
            assign_data = [assign_obj
                           for assign_obj in map(model_to_dict,
                                                 [assign_obj for assign_obj in assign_data])]

            return render(request, 'group-assign-list.html', {'assign_data': assign_data})
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def groupAssignmentCreate(request, group_id):
    try:
        if check_auth_user_id_exist(request):
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
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def groupAssignmentEdit(request, group_id, assign_id):
    try:
        if check_auth_user_id_exist(request):
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
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def groupAssignmentRead(request, group_id, assign_id):
    try:
        if check_auth_user_id_exist(request):
            getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
            # 유저와 그룹이 맵핑 되어있는지 확인 아니면 404 뿜뿜
            assign_data = get_object_or_404(GroupAssignments, id=assign_id)
            context = model_to_dict(assign_data)

            return render(request, 'group-assign-read.html', {'assign_data': context})
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def groupAssignmentDelete(request, group_id, assign_id):
    try:
        if check_auth_user_id_exist(request):
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
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


#######################

def groupSearch(request):
    try:
        if request.method == 'GET':
            group_list = Studygroups.objects.order_by('groupname')
        else:
            group_list = None
        context = {'studygroups': group_list}
        return render(request, "group-search.html", context)
    except:
        return redirect('whatshouldido:error')


def groupCreate(request):
    try:
        if check_auth_user_id_exist(request):
            user_id = get_object_or_404(AuthUser, pk=int(request.session['_auth_user_id']))
            if request.method == "POST":
                group_form = StudygroupsForm(request.POST)
                if group_form.is_valid():
                    group = group_form.save(commit=False)
                    group.grouppasscode = hashlib.sha256(str(group.grouppasscode).encode()).hexdigest()
                    group.groupmaster = user_id
                    group.save()
                    group_mapping = UsersGroupsMapping(
                        useridx=group.groupmaster,
                        groupidx=group)
                    group_mapping.save()
                    print(group.grouppasscode)
                    return redirect('whatshouldido:groupinfo', group_id=group.pk)
            form = StudygroupsForm()
            return render(request, 'group-make.html', {'form': form})
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def groupInfo(request, group_id):
    try:
        group_data = Studygroups.objects.get(groupid=group_id)
        context = model_to_dict(group_data)
    except:
        print(Exception)
        return redirect('whatshouldido:error')

    return render(request, 'group-info.html', {'group_data': context})


def groupManage(request, group_id):
    try:
        if check_auth_user_id_exist(request):
            user_id = getUserObject_or_404(user_id=int(request.session['_auth_user_id']), group_id=group_id)
            group = get_object_or_404(Studygroups, pk=group_id)
            if request.method == "POST":
                group_form = StudygroupsForm(request.POST, instance=group)
                if group_form.is_valid():
                    group = group_form.save(commit=False)
                    group.grouppasscode = hashlib.sha256(str(group.grouppasscode).encode()).hexdigest()
                    group.groupmaster = user_id
                    group.save()
                    print(group.grouppasscode)
                    return redirect('whatshouldido:groupinfo', group_id=group.pk)
            form = StudygroupsForm(instance=group)
            return render(request, 'group-manage.html', {'form': form})
        else:
            return redirect('whatshouldido:index')
    except Exception:
        return redirect('whatshouldido:error')


###############################
def uploadFile(request):
    if request.method == "POST":
        # Fetching the form data
        fileTitle = request.POST["fileTitle"]
        print(fileTitle)
        uploaded_file = request.FILES["uploadedFile"]

        # Saving the information in the database
        file = ArticleFiles(
            field_native_filename=fileTitle,
            uploaded_file=uploaded_file,
            articleid=GroupArticles.objects.get(pk=1),
            uploader=AuthUser.objects.get(pk=5),
            field_encr_filename=hashlib.sha256((fileTitle+str(timezone.now())).encode()).hexdigest(),
            field_file_size=1,
            field_file_type='sad'
        )
        file.save()

    documents = ArticleFiles.objects.all()
    return render(request, "file-upload.html", context={
        "files": documents
    })
