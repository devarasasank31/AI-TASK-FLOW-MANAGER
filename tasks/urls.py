from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task/add/', views.add_task, name='add_task'),
    path('task/edit/<int:pk>/', views.edit_task, name='edit_task'),
    path('task/delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('analytics/', views.analytics, name='analytics'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    # AI endpoints
    path('ai/description/', views.ai_generate_description, name='ai_description'),
    path('ai/priority/', views.ai_suggest_priority, name='ai_priority'),
    path('ai/nlp/', views.ai_parse_nlp, name='ai_nlp'),
    path('ai/subtasks/', views.ai_generate_subtasks, name='ai_subtasks'),
    path('ai/chat/', views.ai_chat, name='ai_chat'),
]
