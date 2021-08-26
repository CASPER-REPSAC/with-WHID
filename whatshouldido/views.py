from django.db.models import Q
from django.forms.models import model_to_dict
from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic.edit import FormView
from .forms import *
from .models import *
from django.http import QueryDict
import hashlib, logging, os


log = logging.getLogger('django')


def check_auth_user_id_exist(request):
    if '_auth_user_id' in dict(request.session):
        return True
    return False


def getUserContents(user_id):
    assign_list, article_list, registered_groups = [], [], list(UsersGroupsMapping.objects.filter(useridx=user_id))
    for mapping_model in registered_groups:
        assign_list += GroupAssignments.objects.filter(groupid=mapping_model.groupidx).order_by('groupassignmentlimit')
        article_list += GroupArticles.objects.filter(groupid=mapping_model.groupidx).order_by('-uploaddate')
    return {"data": {'assign': [x for x in map(model_to_dict, assign_list)],
                     'article': [x for x in map(model_to_dict, article_list)],
                     'groups': [x.groupidx for x in registered_groups]}}


class StudygroupsView(FormView):
    form_class = GroupSearchForm
    template_name = 'group-search.html'

    def render_to_response(self, context, **response_kwargs):
        try:
            if check_auth_user_id_exist:
                user_id = int(self.request.session['_auth_user_id'])
                context.update(getUserContents(user_id))
                response_kwargs.setdefault('content_type', self.content_type)
                return self.response_class(
                    request=self.request,
                    template=self.get_template_names(),
                    context=context,
                    using=self.template_engine,
                    **response_kwargs
                )
        except:
            log.error("Error Occurs : views.StudygroupsView.except 1 | User :"+ self.request.user.id )
            return redirect('whatshouldido:error')

    def form_valid(self, form):
        try:
            if check_auth_user_id_exist:
                user_id = int(self.request.session['_auth_user_id'])
                searchWord = form.cleaned_data['search_word']
                group_list = Studygroups.objects.filter(Q(groupname__icontains=searchWord)).distinct()

                context = {'form': form, 'search_term': searchWord, 'studygroups': group_list}
                context.update(getUserContents(user_id))
                log.info("Search : enter StudygroupsView | User :"+ str(self.request.user.id)+ "Search Word : " + searchWord)
                return render(self.request, self.template_name, context)
            else:
                log.error("Error Occurs : views.StudygroupsView.except 2 | User :"+ self.request.user.id )
                return redirect('whatshouldido:error')
        except:
            log.error("Error Occurs : views.StudygroupsView.except 2 | User :"+ self.request.user.id + "Search Word : " + searchWord)
            return redirect('whatshouldido:error')


def check(request, pk):
    try:
        if check_auth_user_id_exist:
            if request.method == "POST":
                uid = int(request.session['_auth_user_id'])
                if uid != int(request.user.id):
                    log.error("User ID is Tampered |" + str(uid) + " ==> " + request.user.id)
                    return render(request, 'error.html')
                else:
                    input_passcode = hashlib.sha256(str(request.POST.get('passcode')).encode()).hexdigest()
                    try:
                        group = Studygroups.objects.filter(groupid=pk, grouppasscode=input_passcode)
                        try:
                            test = group.get(grouppasscode=input_passcode)
                            print(test)
                        except:
                            log.warning("Invalid passcode | User " + str(uid) + " ==>  Input: " + str(request.Post.get('passcode')))
                            return HttpResponse("입장 코드가 올바르지 않습니다.")
                        context = {'groupss': group}
                        user = AuthUser.objects.get(id=int(uid))
                        groups = Studygroups.objects.get(groupid=pk)
                        mapping = UsersGroupsMapping.objects.get_or_create(useridx=user, groupidx=groups)
                        if not mapping[1]:
                            log.warning("Duplicated Group Join | User " + str(uid) + " ==> Group: " + str(pk))
                            return HttpResponse("이미 가입된 그룹입니다.")
                        else:
                            log.info("User Joined Group | User " + str(uid) + " ==> Group" + str(pk))
                            return render(request, 'join.html', context)
                    except:
                        log.error("Error Occurs : views.check.except 1 | User " + str(uid))
                        return render(request, 'error.html')
        else:
            log.error("Error Occurs : views.check.except 2 | User NONE")
            return redirect('whatshouldido:error')
    except:
        log.error("Unknown Error Occurs : views.check.except 3 | User " + str(uid))
        return redirect('whatshouldido:error')

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
            if request.method == 'GET':
                user_id = int(request.session['_auth_user_id'])
                return render(request, 'calendar.html', context=getUserContents(user_id))
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
        context = {'studygroups': model}
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
            context.update(getUserContents(user_id))
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
            context = {'article_data': article_data}
            context.update(getUserContents(user_id))
            return render(request, 'group-article-list.html', context=context)
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
            comments = GroupArticleComments.objects.filter(articleid=article_id)
            context = {'article_data': context, "comments": comments,
                       'comment_form': GroupArticleCommentsForm()}
            context.update(getUserContents(user_id))
            return render(request, 'group-article-read.html', context=context)
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
            context.update(getUserContents(user_id))
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
            user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
            assign_data = GroupAssignments.objects.filter(groupid=group_id)
            assign_data = [assign_obj
                           for assign_obj in map(model_to_dict,
                                                 [assign_obj for assign_obj in assign_data])]
            context = {'assign_data': assign_data}
            context.update(getUserContents(user_id))
            return render(request, 'group-assign-list.html', context=context)
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
            context.update(getUserContents(user_id))
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
            context.update(getUserContents(user_id))
            return render(request, "group-assign-write.html", context)
        else:
            return redirect('whatshouldido:index')
    except:
        return redirect('whatshouldido:error')


def groupAssignmentRead(request, group_id, assign_id):
    try:
        if check_auth_user_id_exist(request):
            user_id = getUserObject_or_404(int(request.session['_auth_user_id']), group_id)
            # 유저와 그룹이 맵핑 되어있는지 확인 아니면 404 뿜뿜
            assign_data = get_object_or_404(GroupAssignments, id=assign_id)

            context = {'assign_data': model_to_dict(assign_data)}
            context.update(getUserContents(user_id))
            return render(request, 'group-assign-read.html', context=context)
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
            context = {'form': form}
            context.update(getUserContents(user_id))
            return render(request, 'group-make.html', context=context)
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
                    return redirect('whatshouldido:groupinfo', group_id=group.pk)
            form = StudygroupsForm(instance=group)
            context = {'form': form}
            context.update(getUserContents(user_id))
            return render(request, 'group-manage.html', context=context)
        else:
            return redirect('whatshouldido:index')
    except Exception:
        return redirect('whatshouldido:error')


def changeFileName(file):
    pass


###############################
allowed_extension = ('zip')
import re


def uploadFile(request):
    if request.method == "POST":
        uploaded_file = request.FILES["uploadedFile"]
        filename = str(uploaded_file.name).split('.')
        if len(filename) != 2:
            return redirect("whatshouldido:error")
        file_type = filename[-1]
        print(file_type)
        file = ArticleFiles(
            field_native_filename=filename[0]+'.'+file_type,
            articleid=GroupArticles.objects.get(pk=1),
            uploader=AuthUser.objects.get(pk=5),
            field_encr_filename=hashlib.sha256((uploaded_file.name + str(timezone.now())).encode()).hexdigest(),
            field_file_size=1,
            field_file_type=file_type,
            uploaded_file=uploaded_file
        )
        file.uploaded_file.name = file.field_encr_filename
        file.save()

    documents = ArticleFiles.objects.all()
    return render(request, "file-upload.html", context={
        "files": documents
    })
