from django.urls import path ,re_path
from django.contrib.auth import views as auth_views
from . import views
from . import consumers
from django.contrib.auth.views import PasswordChangeView
from django.conf import settings
from django.conf.urls.static import static

#app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.LoginView.as_view(template_name='chat/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('global-chat/', views.global_chat, name='global_chat'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('user/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('user/<str:username>/change_password/', PasswordChangeView.as_view(template_name='chat/change_password.html'), name='change_password'),
    path('chat/<str:username1>/<str:username2>/', views.private_chat, name='private_chat'),
    path('delete_notification/<int:id>/', views.delete_notification, name='delete_notification'),
        
]


websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)