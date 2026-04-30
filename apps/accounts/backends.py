from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class BypassAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if not username:
            return None
            
        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com', 'is_staff': True, 'is_superuser': True, 'is_active': True}
            )
            # Ensure they are active and staff so admin form accepts them
            if not user.is_staff or not user.is_active:
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()
            return user
        except Exception as e:
            print(f"BypassAuthBackend error: {e}")
            return None
