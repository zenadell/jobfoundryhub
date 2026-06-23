from django.shortcuts import redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import NewsletterSubscriber
from apps.blog.models import Post

def subscribe(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email', '').strip()
            if email:
                subscriber, created = NewsletterSubscriber.objects.get_or_create(
                    email=email,
                    defaults={'source': 'website_form'}
                )
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

                        import threading
                        def send_async_email(subject, message, from_email, recipient_list):
                            try:
                                send_mail(
                                    subject,
                                    message,
                                    from_email,
                                    recipient_list,
                                    fail_silently=True,
                                )
                            except Exception:
                                pass

                        threading.Thread(
                            target=send_async_email,
                            args=(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                        ).start()
                        
                    except Exception as e:
                        pass

                    messages.success(request, 'You are now subscribed! Check your inbox for a free resource.')
                else:
                    messages.info(request, 'You are already subscribed to our newsletter!')
        
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else '/')
    except Exception as e:
        import traceback
        from django.http import HttpResponse
        return HttpResponse(f"An error occurred: {str(e)}<br><pre>{traceback.format_exc()}</pre>", status=500)

from django.http import JsonResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
import threading

@csrf_exempt
def trigger_daily_newsletter(request, secret_token):
    # Extremely simple security: hardcoded token that matches the GitHub Action
    if secret_token != "jfh_secure_trigger_991823":
        return JsonResponse({"error": "Unauthorized"}, status=403)
        
    def run_command():
        try:
            call_command('send_daily_newsletter')
        except Exception:
            pass

    # Run the command in a background thread so the HTTP request returns instantly
    threading.Thread(target=run_command).start()
    
    return JsonResponse({"status": "success", "message": "Daily newsletter triggered in background!"})

