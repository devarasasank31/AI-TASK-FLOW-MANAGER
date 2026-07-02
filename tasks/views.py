import json
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Task, ChatMessage
from . import ai_helper


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    context = {
        'tasks': tasks,
        'total': tasks.count(),
        'completed': tasks.filter(status='Completed').count(),
        'in_progress': tasks.filter(status='In Progress').count(),
        'pending': tasks.filter(status='Pending').count(),
    }
    return render(request, 'dashboard.html', context)


@login_required
def add_task(request):
    if request.method == 'POST':
        Task.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            priority=request.POST.get('priority', 'Medium'),
            status=request.POST.get('status', 'Pending'),
            due_date=request.POST.get('due_date') or None,
        )
        messages.success(request, 'Task created successfully!')
        return redirect('dashboard')
    return render(request, 'add_task.html')


@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description', '')
        task.priority = request.POST.get('priority', 'Medium')
        task.status = request.POST.get('status', 'Pending')
        task.due_date = request.POST.get('due_date') or None
        task.save()
        messages.success(request, 'Task updated successfully!')
        return redirect('dashboard')
    return render(request, 'edit_task.html', {'task': task})


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted!')
    return redirect('dashboard')


@login_required
def analytics(request):
    tasks = Task.objects.filter(user=request.user)
    stats = {
        'total': tasks.count(),
        'completed': tasks.filter(status='Completed').count(),
        'in_progress': tasks.filter(status='In Progress').count(),
        'pending': tasks.filter(status='Pending').count(),
        'high': tasks.filter(priority='High').count(),
        'medium': tasks.filter(priority='Medium').count(),
        'low': tasks.filter(priority='Low').count(),
        'overdue': tasks.filter(due_date__lt=date.today(), status__in=['Pending', 'In Progress']).count(),
    }
    try:
        task_list = list(tasks.values('title', 'priority', 'status')[:10])
        insights = ai_helper.get_ai_insights(stats, task_list)
    except Exception:
        insights = "Please add your Anthropic API key in settings.py to enable AI insights."
    return render(request, 'analytics.html', {'stats': stats, 'insights': insights})


@login_required
def chatbot_view(request):
    history = list(ChatMessage.objects.filter(user=request.user).order_by('created_at')[:20])
    return render(request, 'chatbot.html', {'history': history})


# ── AI ENDPOINTS ──────────────────────────────────────────────────────────────

@login_required
@require_POST
def ai_generate_description(request):
    data = json.loads(request.body)
    try:
        desc = ai_helper.generate_description(data.get('title', ''))
        return JsonResponse({'description': desc})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def ai_suggest_priority(request):
    data = json.loads(request.body)
    try:
        priority = ai_helper.suggest_priority(data.get('title', ''), data.get('description', ''))
        return JsonResponse({'priority': priority})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def ai_parse_nlp(request):
    data = json.loads(request.body)
    try:
        result = ai_helper.parse_natural_language(data.get('text', ''))
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def ai_generate_subtasks(request):
    data = json.loads(request.body)
    try:
        subtasks = ai_helper.generate_subtasks(data.get('title', ''), data.get('description', ''))
        return JsonResponse({'subtasks': subtasks})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def ai_chat(request):
    data = json.loads(request.body)
    user_message = data.get('message', '')
    tasks_context = list(Task.objects.filter(user=request.user).values('title', 'priority', 'status', 'due_date')[:10])
    try:
        response = ai_helper.chat_with_ai(user_message, tasks_context)
        ChatMessage.objects.create(user=request.user, message=user_message, response=response)
        return JsonResponse({'response': response})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
