from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class BypassAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Allow any login for an existing user, regardless of password.
        # This completely removes password validation to allow emergency access.
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
