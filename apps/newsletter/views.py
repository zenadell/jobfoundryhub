from django.shortcuts import redirect
from django.contrib import messages
from .models import NewsletterSubscriber

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
            messages.success(request, 'You are now subscribed!')
    return redirect(request.META.get('HTTP_REFERER', '/'))
