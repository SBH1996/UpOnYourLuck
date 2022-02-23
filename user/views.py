from textwrap import fill
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, NewUserForm, UpdateProfileForm, UpdateUserForm #UpdateUserForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Profile

import qrcode


@login_required
def dashboard(request):
    args1 = {
        'current_user': request.user,
    }

    return render(request, 'dashboard.html', args1)


# for visitors going to a user's profile page
def visitor_to_profile(request, username=None):
    if username:
        username_obj = get_object_or_404(User, username=username)
    else:
        messages.error(request, 'No User Found')
        return redirect('welcome_index')
        
    if username_obj.username == request.user.username:
        return redirect('profile')
    context = {
        'profile_username': username_obj.username,
        'payment_link_url': username_obj.profile.payment_link_url,
        'life_story': username_obj.profile.life_story,
        'profile_img': username_obj.profile.profile_img,
        'city': username_obj.profile.city,
        'state': username_obj.profile.state,
    }
    
    return render(request, 'profile_for_visitor.html', context)


# For logged in users to see their own profile page
def profile(request):
    context = {
        'current_user': request.user,
        'payment_link_url': request.user.profile.payment_link_url,
        'life_story': request.user.profile.life_story,
        'profile_img': request.user.profile.profile_img,
        'city': request.user.profile.city,
        'state': request.user.profile.state,
    }
    return render(request, 'profile.html', context)


@login_required()
def update_profile(request):
    if request.method == 'POST':
        p_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        u_form = UpdateUserForm(request.POST, instance=request.user)
        if p_form.is_valid() and u_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your Profile has been updated!')
            return redirect('profile')
    else:
        p_form = UpdateProfileForm(instance=request.user)
        u_form = UpdateUserForm(instance=request.user.profile)

    context = {
            'p_form': p_form,
            'u_form': u_form,
            'current_user': request.user,
            'profile_img': request.user.profile.profile_img,
        }
    return render(request, 'update_profile.html', context)


def register_request(request):
    if request.method == "POST":
        user_form = NewUserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            login(request, user)
            generate_qr_code(request)
            messages.success(request, "Registration successful.")
            return redirect("user_dashboard")

        messages.error(request, "Unsuccessful registration. Invalid information.")
    user_form = NewUserForm()
    return render(request=request, template_name="register.html", context={"register_form": user_form, "user": request.user})


def login_request(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("user_dashboard")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = LoginForm()
    return render(request=request, template_name="login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("welcome_index")


def generate_qr_code(request):
    DOMAIN = 'http://127.0.0.1:8000/'
    profile_url = request.user.profile.profile_url
    user_profile_full_url = DOMAIN + profile_url
    qr_img = qrcode.make(user_profile_full_url)
    qr_img.save('media/qr_code/' + request.user.username + '.jpg')
    request.user.profile.qr_code_img = request.user.username + '.jpg'
