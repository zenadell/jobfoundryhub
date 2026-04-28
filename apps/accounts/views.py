from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        username  = request.POST.get('username')
        email     = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'accounts/register.html')
        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, 'Welcome! Your account has been created.')
        return redirect('core:home')
    return render(request, 'accounts/register.html')


def user_login(request):
    if request.method == 'POST':
        email    = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'accounts:dashboard'))
        messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    return redirect('core:home')


@login_required
def dashboard(request):
    from apps.accounts.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    saved_jobs = profile.saved_jobs.filter(is_active=True).select_related('company')[:6]
    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'saved_jobs': saved_jobs,
    })
