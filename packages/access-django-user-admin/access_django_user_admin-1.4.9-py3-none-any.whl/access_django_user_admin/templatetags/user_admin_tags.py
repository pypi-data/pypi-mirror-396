from django import template
from django.contrib.auth import get_user_model

register = template.Library()

@register.filter
def get_existing_user(username):
    User = get_user_model()
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None