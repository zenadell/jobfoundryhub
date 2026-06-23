from django.shortcuts import redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import NewsletterSubscriber
from apps.blog.models import Post

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                try:
                    latest_post = Post.live.order_by('-published_at').first()
                    
                    if latest_post:
                        post_url = request.build_absolute_uri(latest_post.get_absolute_url())
                        subject = 'Welcome to JobFoundryHub! Here is your free resource'
                        message = (
                            f"Hi there!\n\n"
                            f"Thank you for subscribing to JobFoundryHub.\n\n"
                            f"As promised, here is an excellent resource to help you in your career:\n\n"
                            f"Read it here: {post_url}\n\n"
                            f"We'll be sending you the best daily job updates directly to your inbox. Stay tuned!\n\n"
                            f"Best regards,\nThe JobFoundryHub Team"
                        )
                    else:
                        subject = 'Welcome to JobFoundryHub!'
                        message = (
                            f"Hi there!\n\n"
                            f"Thank you for subscribing to JobFoundryHub.\n\n"
                            f"We'll be sending you the best daily job updates directly to your inbox. Stay tuned!\n\n"
                            f"Best regards,\nThe JobFoundryHub Team"
                        )

                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

                messages.success(request, 'You are now subscribed! Check your inbox for a free resource.')
            else:
                messages.info(request, 'You are already subscribed to our newsletter!')
                
    return redirect(request.META.get('HTTP_REFERER', '/'))
