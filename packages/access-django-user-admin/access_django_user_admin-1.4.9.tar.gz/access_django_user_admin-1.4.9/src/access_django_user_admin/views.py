from django.views.generic import FormView, TemplateView, View
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.cache import cache_control
from .access_django_user_admin_api_service import djangouser
from .forms import UserCreationForm
import string
import random
import requests
import os
from allauth.socialaccount.models import SocialAccount
from django.http import HttpRequest, FileResponse
from django.http import HttpResponse
from django.conf import settings
from .utils import get_base_template, get_current_app_name


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)
def favicon(request: HttpRequest) -> HttpResponse:
    file = open(settings.STATIC_ROOT + '/access_django_user_admin/img/favicon.ico', 'rb')
    return FileResponse(file)

def admins_check(user):
    return (user.is_superuser or
            user.has_perm('auth.add_user') or
            user.groups.filter(name='account-admins').exists())

#@login_required
def debug_user_groups(request):
    groups = request.user.groups.all()
    group_names = [g.name for g in groups]
    has_add_user_perm = request.user.has_perm('auth.add_user')
    return HttpResponse(f"User: {request.user.username}, Groups: {group_names}, "
                        f"Superuser: {request.user.is_superuser}, "
                        f"Can Add Users: {has_add_user_perm}")

def unprivileged_view(request):
    return render(request, 'access_django_user_admin/unprivileged.html', {
        'message': "You must be a member of 'account-admins' or be able to edit users to access this feature."
    })

class IndexView(UserPassesTestMixin, TemplateView):
    template_name = 'access_django_user_admin/access_django_user_admin.html'

    def test_func(self):
        return admins_check(self.request.user)

    def handle_no_permission(self):
        return redirect('access_django_user_admin:unprivileged')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = get_base_template()
        context['page'] = 'access_django_user_admin'
        return context

    def get(self, request, *args, **kwargs):
        # Handle search functionality
        query = request.GET.get('q', '')
        search_results = []

        if query and len(query) >= 2:
            try:
                api_results = djangouser.search_users(query)

                # Transform API results to match django db needs
                users_list = api_results.get('result', [])
                search_results = []

                if users_list:
                    print(f"Sample user from API: {users_list[0]}")

                # Build a lookup for Django users by portal_login/username
                django_users = {u.username: u for u in User.objects.all()}

                for user in users_list:
                    portal_login = user.get('portal_login', '')
                    django_user = django_users.get(portal_login)
                    is_active = django_user.is_active if django_user else False
                    user_dict = {
                        'portal_login': portal_login,
                        'first_name': user.get('first_name', ''),
                        'last_name': user.get('last_name', ''),
                        'email': user.get('email', ''),
                        'is_active': is_active,
                    }
                    search_results.append(user_dict)

                # Print
                if search_results:
                    print(f"First search result being sent to template: {search_results[0]}")

            except Exception as e:
                messages.error(request, f"API Error: {str(e)}")

        # List of existing users as dicts for sorting
        all_users = list(User.objects.all())
        def current_user_sort_key(u):
            name = (u.first_name + u.last_name).lower()
            return (not u.is_active, name)
        sorted_current_users = sorted(all_users, key=current_user_sort_key)

        # Sort search_results: active users first, then by name
        def user_sort_key(u):
            name = (u.get('first_name', '') + u.get('last_name', '')).lower()
            return (not u.get('is_active', False), name)

        search_results = sorted(search_results, key=user_sort_key)

        # Build context
        context = self.get_context_data(
            users=sorted_current_users,
            search_results=search_results
        )

        return self.render_to_response(context)


class AddUserView(UserPassesTestMixin, FormView):
    model = User
    form_class = UserCreationForm
    template_name = 'access_django_user_admin/add_user.html'
    success_url = reverse_lazy('access_django_user_admin:index')

    def test_func(self):
        return admins_check(self.request.user)

    def handle_no_permission(self):
        return redirect('access_django_user_admin:unprivileged')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_groups'] = Group.objects.all().order_by('name')
        context['base_template'] = get_base_template()  # ADD THIS LINE
        context['page'] = 'access_django_user_admin'
        return context

    def get_initial(self):
        # Initialize form with data from GET parameters
        initial = super().get_initial()

        # Map portal_login to username
        initial['username'] = self.request.GET.get('portal_login', '')

        # Map other fields directly
        initial['first_name'] = self.request.GET.get('first_name', '')
        initial['last_name'] = self.request.GET.get('last_name', '')
        initial['email'] = self.request.GET.get('email', '')
        initial['is_active'] = True

        return initial

    def generate_secure_password(self, username):
        """Generate a secure password that passes Django validation."""
        while True:
            chars = string.ascii_letters + string.digits + "!@#$%^&*()_-+=<>?"
            password = ''.join(random.choice(chars) for _ in range(16))

            if (any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                any(c.isdigit() for c in password) and
                any(c in "!@#$%^&*()_-+=<>?" for c in password)):

                try:
                    validate_password(password, User(username=username))
                    return password
                except ValidationError:
                    continue

    def form_valid(self, form):
        user = form.save(commit=False)

        # Generate secure password
        secure_password = self.generate_secure_password(user.username)
        user.set_password(secure_password)

        # Save user
        user.save()

        # Add user to available groups
        group_ids = self.request.POST.getlist('groups')
        for group_id in group_ids:
            try:
                group = Group.objects.get(id=group_id)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass

        # Verify CILogon provider exists
        from allauth.socialaccount.models import SocialApp

        # Check if provider exists - try both 'CILogon' and 'cilogon'
        provider_exists = SocialApp.objects.filter(provider__iexact='cilogon').exists()

        if provider_exists:
            try:
                provider_name = SocialApp.objects.filter(provider__iexact='cilogon').first().provider

                # Create social account
                social_account = SocialAccount.objects.create(
                    user=user,
                    provider=provider_name,
                    uid=f"{user.username}@access-ci.org"
                )
                messages.success(
                    self.request,
                    f"User '{user.username}' created successfully with social account linked."
                )
            except Exception as e:
                import traceback
                print(f"Error creating social account: {str(e)}")
                print(traceback.format_exc())
                messages.warning(
                    self.request,
                    f"User '{user.username}' created, but linking to CILogon failed: {str(e)}"
                )
        else:
            messages.warning(
                self.request,
                f"User '{user.username}' created, but CILogon provider not found in database. "
                f"Please add it in the admin interface."
            )

        # Success URL
        return redirect(self.success_url)



class EditUserView(UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'access_django_user_admin/edit_user.html'
    fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']
    success_url = reverse_lazy('access_django_user_admin:index')

    def get_object(self, queryset=None):
        # Explicitly get the user by ID from the URL
        user_id = self.kwargs.get('pk')
        user = get_object_or_404(User, id=user_id)
        print(f"EditUserView: Retrieved user {user.username} (ID: {user_id})")
        return user

    def test_func(self):
        return admins_check(self.request.user)

    def handle_no_permission(self):
        return redirect('access_django_user_admin:unprivileged')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_groups'] = Group.objects.all()
        context['user_groups'] = self.object.groups.all()
        context['base_template'] = get_base_template()  # ADD THIS LINE
        context['page'] = 'access_django_user_admin'    # ADD THIS LINE
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        # Handle group membership
        user = self.object
        user.groups.clear()

        # Add user to selected groups
        group_ids = self.request.POST.getlist('groups')
        for group_id in group_ids:
            group = Group.objects.get(id=group_id)
            user.groups.add(group)

        messages.success(self.request, f'User {user.username} has been updated successfully.')
        return response

class DeleteUserView(UserPassesTestMixin, View):
    def test_func(self):
        return admins_check(self.request.user)

    def handle_no_permission(self):
        return redirect('access_django_user_admin:unprivileged')

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        username = user.username

        # Delete the user
        user.delete()

        messages.success(request, f"User '{username}' has been deleted successfully.")
        return redirect('access_django_user_admin:index')
