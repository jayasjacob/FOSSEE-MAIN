from os import listdir, path, sep, makedirs, remove
from .forms import (
            UserRegistrationForm, UserLoginForm,
            ProfileForm, AnimationProposal,
            CommentForm, UploadAnimationForm
            )
from .models import (
            Profile, User, AnimationStats,
            has_profile, Animation, Comment,
            Category
            )
from datetime import datetime, date
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.files.uploadhandler import FileUploadHandler
from django.db.models import F, Subquery, OuterRef, Q
from zipfile import ZipFile
from textwrap import dedent
from requests import get
from random import sample
from .send_mails import send_email
import datetime as dt
import shutil
try:
    from StringIO import StringIO as string_io
except ImportError:
    from io import BytesIO as string_io


def makepath(proposal_data, reject=None):
    if not path.exists(path.join(settings.MEDIA_ROOT,
                       proposal_data.category.name)):
        makedirs(path.join(settings.MEDIA_ROOT,
                 proposal_data.category.name))

    if reject:
        shutil.rmtree(path.join(
                     settings.MEDIA_ROOT, proposal_data.category.name,
                     proposal_data.title.replace(" ", "_")
                     + str(proposal_data.id)))
    else:
        makedirs(path.join(settings.MEDIA_ROOT, proposal_data.category.name,
                 proposal_data.title.replace(" ", "_")
                 + str(proposal_data.id)))


def check_repo(link):
    try:
        return (get(link).status_code == 200)
    except:
        return False

def is_email_checked(user):
    if hasattr(user, 'profile'):
        return True if user.profile.is_email_verified else False
    else:
        return False


def is_superuser(user):
    return user.is_superuser


def index(request):
    '''Landing Page'''

    user = request.user
    form = UserLoginForm()
    if user.is_authenticated() and is_email_checked(user):
        if user.groups.filter(name='reviewer').exists:
            return redirect('/proposal_status/')
        return redirect('/view_profile/')
    elif request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data
            login(request, user)
            if is_superuser(user):
                return redirect("/admin")
            if user.groups.filter(name='reviewer').exists():
                return redirect('/proposal_status/')
            return redirect('/view_profile/')
    anime = AnimationStats.objects.filter(animation__status='released').order_by('-id')[:5]
    return render(request, "fossee_manim/index.html", {"form": form,
                    "anime" : anime
                })


def is_reviewer(user):
    '''Check if the user is having reviewer rights'''
    return user.groups.filter(name='reviewer').exists()


def user_login(request):
    '''User Login'''
    user = request.user
    categories = Category.objects.all()
    if is_superuser(user):
        return redirect('/admin')
    if user.is_authenticated():
        if user.groups.filter(name='reviewer').count() > 0:
            return redirect('/view_profile/')
        return redirect('/view_profile/')

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data
            login(request, user)
            if user.groups.filter(name='reviewer').count() > 0:
                return redirect('/view_profile/')
            return redirect('/how_to/')
        else:
            return render(request, 'fossee_manim/login.html', {"form": form})
    else:
        form = UserLoginForm()
        return render(request, 'fossee_manim/login.html', {"form": form,
                        'categories': categories })


def user_logout(request):
    '''Logout'''
    logout(request)
    return render(request, 'fossee_manim/logout.html')


def activate_user(request, key=None):
    user = request.user
    if is_superuser(user):
        return redirect("/admin")
    if key is None:
        if user.is_authenticated() and user.profile.is_email_verified==0 and \
        timezone.now() > user.profile.key_expiry_time:
            status = "1"
            Profile.objects.get(user_id=user.profile.user_id).delete()
            User.objects.get(id=user.profile.user_id).delete()
            return render(request, 'fossee_manim/activation.html',
                        {'status':status})
        elif user.is_authenticated() and user.profile.is_email_verified==0:
            return render(request, 'fossee_manim/activation.html')
        elif user.is_authenticated() and user.profile.is_email_verified:
            status = "2"
            return render(request, 'fossee_manim/activation.html',
                        {'status':status})
        else:
            return redirect('/register/')

    try:
        user = Profile.objects.get(activation_key=key)
    except:
        return redirect('/register/')

    if key == user.activation_key:
        user.is_email_verified = True
        user.save()
        status = "0"
    else:
        logout(request)
        return redirect('/logout/')
    return render(request, 'fossee_manim/activation.html',
                {"status": status})


def user_register(request):
    '''User Registration form'''
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username, password, key = form.save()
            new_user = authenticate(username=username, password=password)
            login(request, new_user)
            user_position = request.user.profile.position
            send_email(
                       request, call_on='Registration',
                       key=key
                      )

            return render(request, 'fossee_manim/activation.html')
        else:
            if request.user.is_authenticated():
                return redirect('/view_profile/')
            categories = Category.objects.all()
            return render(
                request, "fossee_manim/registration/register.html",
                {"form": form, 'categories': categories})
    else:
        categories = Category.objects.all()
        if request.user.is_authenticated() and is_email_checked(request.user):
            return redirect('/view_profile/')
        elif request.user.is_authenticated():
            return render(request, 'fossee_manim/activation.html')
        form = UserRegistrationForm()
    return render(request, "fossee_manim/registration/register.html", {'form': form, 'categories': categories})


@login_required
def view_profile(request):
    """ view instructor and coordinator profile """
    user = request.user
    categories = Category.objects.all()
    if is_superuser(user):
        return redirect('/admin')
    if is_email_checked(user) and user.is_authenticated():
        return render(request, "fossee_manim/view_profile.html",
                      {'categories': categories})
    else:
        if user.is_authenticated():
            return render(request, 'fossee_manim/activation.html')
        else:
            try:
                logout(request)
                return redirect('/login/')
            except:
                return redirect('/register/')


@login_required
def edit_profile(request):
    """ edit profile details facility for reviewer and contributor """

    user = request.user
    categories = Category.objects.all()
    if is_superuser(user):
        return redirect('/admin')
    if is_email_checked(user) and user.is_authenticated():
        if is_reviewer(user):
            template = 'fossee_manim/view_profile.html'
        else:
            template = 'fossee_manim/proposal_status.html'
    else:
        try:
            logout(request)
            return redirect('/login/')
        except:
            return redirect('/register/')

    context = {'template': template}
    if has_profile(user) and is_email_checked(user):
        profile = Profile.objects.get(user_id=user.id)
    else:
        profile = None

    if request.method == 'POST':
        form = ProfileForm(request.POST, user=user, instance=profile)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user = user
            form_data.user.first_name = request.POST['first_name']
            form_data.user.last_name = request.POST['last_name']
            form_data.user.save()
            form_data.save()

            return render(
                        request, 'fossee_manim/profile_updated.html',
                        {'categories': categories}
                        )
        else:
            context['form'] = form
            return render(request, 'fossee_manim/edit_profile.html', context)
    else:
        form = ProfileForm(user=user, instance=profile)
        return render(request, 'fossee_manim/edit_profile.html', {'form': form,
                      'categories': categories}
                      )


@login_required
def send_proposal(request):
    user = request.user
    categories = Category.objects.all()
    if is_email_checked(user) and user.is_authenticated():
        if request.method == 'POST':
            form = AnimationProposal(request.POST)
            if form.is_valid():
                form_data = form.save(commit=False)
                form_data.contributor = user
                form_data.status = "pending"
                if check_repo(form_data.github):
                    form_data.save()
                    form.save_m2m()
                    # makepath(form_data)
                else:
                    messages.warning(request, 'Please enter valid github details')
                    return render(request, 'fossee_manim/send_proposal.html',
                                {'form': form, 'categories': categories})
            return redirect('/proposal_status/')
        else:
            form = AnimationProposal()
            return render(request, 'fossee_manim/send_proposal.html',
                      {'form': form, 'categories': categories})
    else:
        return redirect('/register/')


@login_required
def proposal_status(request):
    user = request.user
    if is_email_checked(user) and user.is_authenticated():
        profile = Profile.objects.get(user_id=user)
        anime = {}
        anime_list = {}
        categories = Category.objects.all()
        if profile.position == 'contributor':
            anime = Animation.objects.filter(contributor_id=user)
        else:
            anime_list = Animation.objects.order_by('-created')
        return render(request, 'fossee_manim/proposal_status.html',
                  {'anime': anime, 'anime_list': anime_list,
                   'categories': categories})
    else:
        return redirect('/login/')


@login_required
def edit_proposal(request, proposal_id=None):
    user = request.user
    if is_email_checked(user) and user.is_authenticated():
        comment_form = CommentForm()
        proposal = Animation.objects.get(id=proposal_id)
        proposal_form = AnimationProposal(instance=proposal)
        upload_form = UploadAnimationForm()
        categories = Category.objects.all()
        video = AnimationStats.objects.filter(animation=proposal_id)
        try:
            comments = Comment.objects.filter(animation_id=proposal_id).order_by(
                                        '-created_date'
                                        )
        except:
            comments = None
        if request.method == 'POST':
            text = request.POST.get('comment')
            status1 = request.POST.get('release')
            status2 = request.POST.get('rejected')

            if status1 or status2 is not None:
                if status1:
                    proposal.status = 'released'
                    send_email(request, call_on='released',
                            contributor=proposal.contributor)
                else:
                    proposal.status = 'rejected'
                    makepath(proposal, reject=1)
                    send_email(request, call_on='rejected',
                            contributor=proposal.contributor)
                proposal.reviewer = user
                proposal.save()
                return redirect('/proposal_status/')

            if text is not None:
                comment_form = CommentForm(request.POST)
                form_data = comment_form.save(commit=False)
                form_data.commentor = user
                form_data.animation = proposal
                form_data.animation_status = proposal.status
                if user.profile.position == 'reviewer':
                    proposal.status = 'changes'
                    proposal.save()
                    send_email(request, call_on='changes',
                            contributor=proposal.contributor,
                            proposal=proposal)
                form_data.save()
                return redirect('/edit_proposal/{}'.format(proposal_id))
            proposal_form = AnimationProposal(request.POST, instance=proposal)
            if proposal_form.is_valid():
                p_f = proposal_form.save(commit=False)
                p_f.contributor = user
                p_f.save()
                proposal_form.save_m2m()
        else:
            if user.profile.position == 'contributor':
                if user.id != proposal.contributor_id:
                    return redirect('/logout/')
    else:
        return redirect('/register/')

    if comments is not None:
            #Show upto 12 Workshops per page
            paginator = Paginator(comments, 9)
            page = request.GET.get('page')
            try:
                comments = paginator.page(page)
            except PageNotAnInteger:
            #If page is not an integer, deliver first page.
                comments = paginator.page(1)
            except EmptyPage:
                #If page is out of range(e.g 999999), deliver last page.
                comments = paginator.page(paginator.num_pages)
    return render(request, 'fossee_manim/edit_proposal.html',
                      {'proposal_form': proposal_form,
                       "comments": comments,
                       "comment_form": comment_form,
                        "upload_form": upload_form,
                        'video': video,
                        'categories': categories})


def search(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        word = request.POST.get('sbox')
        anime_list = AnimationStats.objects.filter(
            Q(animation__title__contains=word) | Q(animation__description__contains=word)
            | Q(animation__category__name__contains=word), animation__status='released')
        
    return render(request, 'fossee_manim/search_results.html',
                  {'s_result': anime_list, 'categories': categories})


@login_required
def upload_animation(request, proposal_id=None):
    user = request.user
    if is_email_checked(user) and user.is_authenticated():
        if request.method == 'POST':
            proposal = Animation.objects.get(id=proposal_id)
            anim_stats = UploadAnimationForm(request.POST or None,
                                            request.FILES or None)
            if anim_stats.is_valid():
                anim = AnimationStats.objects.filter(
                        animation=proposal)
                if anim.exists():
                    anobj = anim.first()
                    try:
                        remove(anobj.thumbnail.path)
                    except:
                        pass
                    remove(anobj.video_path.path)
                    anobj.delete()
                    anobj = AnimationStats.objects.create(
                        animation=proposal, video_path=request.FILES['video_path'])
                else:
                    anobj = AnimationStats.objects.create(
                        animation=proposal, video_path=request.FILES['video_path'])
                anobj._create_thumbnail()

            return render(request, 'fossee_manim/upload_success.html')
        else:
            return redirect('/view_profile/')
    else:
        return redirect('/login/')


def video(request, aid=None):
    user = request.user
    video = AnimationStats.objects.filter(id=aid, animation__status="released")
    if len(video):
        comment_form = CommentForm()
        # if views crosses limit comment the line below
        video.update(views=F('views')+1)
        video.update(like=F('like')+1)
        anim_list = AnimationStats.objects.filter(animation__status="released")
        suggestion_list = [x for x in anim_list if (
            x.animation.category == video[0].animation.category)]
        reviewer_id = video[0].animation.reviewer.id
        comment_list = Comment.objects.filter(animation=video[0].animation)
        comments = [x for x in comment_list if x.animation.status !=
                    ('pending' or 'changes')]
        if request.method == 'POST':
            if is_email_checked(user):
                comment_form = CommentForm(request.POST)
                form_data = comment_form.save(commit=False)
                form_data.commentor = user
                form_data.animation = video[0].animation
                form_data.animation_status = video[0].animation.status
                form_data.save()
                return redirect('/video/{}'.format(aid))
            else:
                return redirect('/login/')
    else:
        return redirect('/view_profile/')
            
    if len(suggestion_list)>3:
        suggestion_list = sample(suggestion_list, 3)
    else:
        suggestion_list = [x for x in anim_list if x.id != int(aid)][:3]
    categories = Category.objects.all()
    return render(request, 'fossee_manim/video.html',
                  {'video': video, 'categories': categories,
                   'reco': suggestion_list,
                   "comment_form": comment_form,
                   'comments': comments})


def search_category(request, cat=None):
    cat_id = Category.objects.get(name=cat)
    anim_list = AnimationStats.objects.filter(animation__status="released")
    cat_video_list = [x for x in anim_list if (x.animation.category == cat_id)]
    categories = Category.objects.all()
    return render(request, 'fossee_manim/categorical_list.html',
                  {'categorial_list': cat_video_list, 'categories': categories
                   })


def how_to(request):
    user = request.user
    categories = Category.objects.all()
    if is_email_checked(user) and user.is_authenticated():
        return render(request, 'fossee_manim/how_to.html', {'categories': categories})
    else:
        return redirect('/register/')