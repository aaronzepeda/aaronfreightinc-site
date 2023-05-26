from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from .forms import NewUserForm


def home(request):
    return redirect('/')
def index(request):
    args = {}
    return render(request, 'index/home.html', args)
#    return HttpResponse("Hello, world. You're at the polls index.")

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return HttpResponseRedirect(reverse('invoices:index'))
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request=request, template_name="index/register.html", context={"register_form":form})

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return HttpResponseRedirect(reverse('invoices:index'))
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    if request.user.is_authenticated:
        return redirect(reverse('invoices:index'))
    form = AuthenticationForm()
    return render(request=request, template_name="index/login.html", context={"login_form":form})


def logout_request(request):
    logout(request)
    return redirect(reverse('index:index'))