from django.shortcuts import render, redirect
from django.http import HttpResponse

def home(request):
    return redirect('/')
def index(request):
    args = {

    }
    return render(request, 'home.html', args)
#    return HttpResponse("Hello, world. You're at the polls index.")