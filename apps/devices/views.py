"""
Views for the Devices app
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages


@login_required(login_url='/login/')
@require_http_methods(["GET"])
def dashboard(request):
    """
    Main energy dashboard view.

    Renders the energy management dashboard with real-time statistics
    and device monitoring. Requires authentication.
    """
    context = {
        'page_title': 'Energy Dashboard',
        'user': request.user,
    }
    return render(request, 'dashboard.html', context)


@require_http_methods(["GET"])
def dashboard_demo(request):
    """
    Demo dashboard with mock data (no authentication required).

    Useful for showcasing the interface without requiring login.
    """
    context = {
        'page_title': 'Energy Dashboard - Demo',
        'demo_mode': True,
    }
    return render(request, 'dashboard.html', context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    User login view.

    GET: Display login form
    POST: Process login credentials
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            context = {
                'error': 'Invalid username or password. Please try again.',
                'username': username,
            }
            return render(request, 'login.html', context)

    return render(request, 'login.html')


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    User logout view.

    Logs out the user and redirects to login page.
    """
    auth_logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')


@login_required(login_url='/login/')
@require_http_methods(["GET"])
def test_devices(request):
    """Test page for debugging device queries."""
    return render(request, 'test_devices.html')
