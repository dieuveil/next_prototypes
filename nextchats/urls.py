from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("chat", views.chat_view, name='chat'),
    path('login/', views.login_page, name='login_page'),    
    path('register/', views.register_page, name='register'),
    path('user_logout', views.user_logout, name='user_logout'),
    #path("welcome", views.chat_view2, name='welcome'),
]