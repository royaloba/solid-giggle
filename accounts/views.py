from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login after registration
            messages.success(request, "Registration successful! Welcome to Stylinsole.")
            return redirect('store:home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            # If they were trying to checkout before logging in, send them back there
            next_url = request.GET.get('next', 'store:home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
        
    # Apply Tailwind classes to login form dynamically
    for field in form.fields.values():
        field.widget.attrs['class'] = 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-black outline-none transition'

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out securely.")
    return redirect('store:home')