from django.urls import path
from . import views
from .views import AddUserView

app_name = 'access_django_user_admin'

'''Django URL Configuration for Access_Django_User_Admin app.'''

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add/', views.AddUserView.as_view(), name='add_user'),
    path('edit-user/<int:pk>/', views.EditUserView.as_view(), name='edit_user'),
    path('delete-user/<int:pk>/', views.DeleteUserView.as_view(), name='delete_user'),
    path('unprivileged/', views.unprivileged_view, name='unprivileged'),
    path('favicon.ico', views.favicon, name='favicon'),
]

