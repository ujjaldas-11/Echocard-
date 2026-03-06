from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django import forms




class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'username'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'password'
        })
    )


class RegistrationForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'username'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'Email'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'password'
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-dark text-light border-secondary',
            'placeholder': 'confirm password'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('username already taken.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password =cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError('Password does not match')
        return cleaned_data






def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username = form.cleaned_data['username'],
                email = form.cleaned_data['email'],
                password = form.cleaned_data['password']
            )

            login(request, user)
            messages.success(request, f'✅ welcome {user.username}!')
            return redirect('home')
    else:
        form = RegistrationForm
        
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password']
            )

            if user:
                login(request, user)
                messages.success(request, f'✅ welcome {user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST': 
        logout(request)
        messages.success(request, f'✅ Logged out successfully')
    return redirect('login')





    