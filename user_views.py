from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth
from django.http import Http404
from .models import SoloUser


def login(request):
    if request.method == 'POST':
        username = request.POST['login']
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect("/")
        else:
            return render(request, 'solo_settings.html', {})
    raise Http404
