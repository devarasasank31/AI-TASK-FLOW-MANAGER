from django.contrib import admin
from .models import Task, ChatMessage

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'status', 'due_date']
    list_filter = ['priority', 'status']
    search_fields = ['title']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'created_at']
