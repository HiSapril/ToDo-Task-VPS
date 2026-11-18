from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.views.decorators.http import require_http_methods
from todo.forms import TaskForm
from todo.models import Task


@login_required
def todopage(request):
    """Landing page redirecting to task list."""
    return redirect('list_task')


@login_required
def list(request):
    """Display only tasks belonging to the currently logged in user."""
    objects = Task.objects.filter(user=request.user)
    return render(request, "todo/list_task.html", {"objects": objects})


@login_required
def create(request):
    """Create a new task for the current user."""
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect("list_task")
    else:
        form = TaskForm()
    return render(request, 'todo/create_task.html', {'form': form})


@login_required
def update(request, pk):
    """Update an existing task owned by the current user."""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("list_task")
    else:
        form = TaskForm(instance=task)

    return render(request, "todo/update_task.html", {"form": form, "task": task})


@login_required
@require_http_methods(["POST"])
def delete(request, pk):
    """Delete a task owned by the current user (POST request only)."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    return redirect("list_task")


def register(request):
    """Register a new user using Django standard UserCreationForm."""
    if request.user.is_authenticated:
        return redirect("list_task")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("list_task")
    else:
        form = UserCreationForm()

    return render(request, "todo/register.html", {"form": form})


def user_logout(request):
    """Log out user and redirect to login page (supports both POST and GET)."""
    logout(request)
    return redirect("login")
