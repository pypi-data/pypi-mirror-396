# access_django_user_admin/utils.py
from django.conf import settings
import os

def get_base_template():
    """
    Returns the base template
    """
    return 'web/base_nav_full.html'


def get_current_app_name():
    return getattr(settings, 'APP_NAME', 'Unknown App')


