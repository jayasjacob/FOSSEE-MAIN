from django.shortcuts import render
from .forms import (
            UserRegistrationForm, UserLoginForm,
            ProfileForm, AnimationProposal, 
            CommentForm
            )
from .models import (
            Profile, User, AnimationStats,
            has_profile, Animation, Comment
            )
from datetime import datetime, date
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.utils import timezone
from .send_mails import send_email
from django.http import HttpResponse, HttpResponseRedirect
from textwrap import dedent
from django.conf import settings
from os import listdir, path, sep
from zipfile import ZipFile
from django.contrib import messages
from django.db.models import Q
import datetime as dt
import os
try:
    from StringIO import StringIO as string_io
except ImportError:
    from io import BytesIO as string_io


def check_repo(link):
    return True if 'github.com' in link else False


def is_email_checked(user):
    if hasattr(user, 'profile'):
        return True if user.profile.is_email_verified else False
    else:
        return False


def is_superuser(user):
    return True if user.is_superuser else False


def index(request):
    '''Landing Page'''

    user = request.user
    form = UserLoginForm()
    if user.is_authenticated() and is_email_checked(user):
        if user.groups.filter(name='reviewer').count() > 0:
            return redirect('/view_profile/')
        return redirect('/view_profile/')
    elif request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data
            login(request, user)
            if is_superuser(user):
                return redirect("/admin")
            if user.groups.filter(name='reviewer').count() > 0:
                return redirect('/view_profile/')
            return redirect('/view_profile/')

    return render(request, "fossee_manim/index.html", {"form": form})


def is_reviewer(user):
    '''Check if the user is having reviewer rights'''
    return True if user.groups.filter(name='reviewer').count() > 0 else False


def user_login(request):
    '''User Login'''
    user = request.user
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
            return redirect('/view_profile/')
        else:
            return render(request, 'fossee_manim/login.html', {"form": form})
    else:
        form = UserLoginForm()
        return render(request, 'fossee_manim/login.html', {"form": form})


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
            return render(
                request, "fossee_manim/registration/register.html",
                {"form": form}
                )
    else:
        if request.user.is_authenticated() and is_email_checked(request.user):
            return redirect('/view_profile/')
        elif request.user.is_authenticated():
            return render(request, 'fossee_manim/activation.html')
        form = UserRegistrationForm()
    return render(request, "fossee_manim/registration/register.html", {"form": form})


@login_required
def view_profile(request):
    """ view instructor and coordinator profile """
    user = request.user
    if is_superuser(user):
        return redirect('/admin')
    if is_email_checked(user) and user.is_authenticated():
        return render(request, "fossee_manim/view_profile.html")
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
    if is_superuser(user):
        return redirect('/admin')
    if is_email_checked(user):
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
                        request, 'fossee_manim/profile_updated.html'
                        )
        else:
            context['form'] = form
            return render(request, 'fossee_manim/edit_profile.html', context)
    else:
        form = ProfileForm(user=user, instance=profile)
        return render(request, 'fossee_manim/edit_profile.html', {'form': form}
                      )


@login_required
def send_proposal(request):
    user = request.user
    if request.method == 'POST':
        form = AnimationProposal(request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.contributor = user
            form_data.status = "pending" 
            if check_repo(form_data.github):
                form_data.save()
                form.save_m2m()
            else:
                messages.warning(request, 'Please enter valid github details')
                return render(request, 'fossee_manim/send_proposal.html',
                      {'form': form})
        return redirect('/proposal_status/')
    else:
        form = AnimationProposal()
        return render(request, 'fossee_manim/send_proposal.html',
                      {'form': form})


@login_required
def proposal_status(request):
    user = request.user
    profile = Profile.objects.get(user_id=user)
    anime = {}
    anime_list = {}
    if profile.position == 'contributor':
        anime = Animation.objects.filter(contributor_id=user)
    else:
        anime_list = Animation.objects.filter(Q(status='pending') |
                                              Q(status='changes'))
    return render(request, 'fossee_manim/proposal_status.html',
                  {'anime': anime, 'anime_list': anime_list})


@login_required
def edit_proposal(request, proposal_id=None):
    user = request.user
    comment_form = CommentForm()
    proposal = Animation.objects.get(id=proposal_id)
    proposal_form = AnimationProposal(instance=proposal)
    try:
        comments = Comment.objects.all().order_by('-created_date')
    except:
        comments = None
    if request.method == 'POST':
        text = request.POST.get('comment')
        s1 = request.POST.get('release')
        s2 = request.POST.get('rejected')

        if s1 or s2 is not None:
            if s1:
                proposal.status = 'released'
                proposal.reviewer = user
                proposal.save()
                send_email(request, call_on='released',
                contributor=proposal.contributor)
            else:
                proposal.status = 'rejected'
                proposal.reviewer = user
                proposal.save()
                send_email(request, call_on='rejected',
                contributor=proposal.contributor)
            return redirect('/proposal_status/')

        if text is not None:
            comment_form = CommentForm(request.POST)
            form_data = comment_form.save(commit=False)
            form_data.commentor = user
            form_data.animation = proposal
            if user.profile.position == 'reviewer':
                proposal.status = 'changes'
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
                        "comment_form": comment_form})


def search(request):
    if request.method == 'POST':
        word = request.POST.get('sbox')
        
    return render(request, 'fossee_manim/search_results.html')

