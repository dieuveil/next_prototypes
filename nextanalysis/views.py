from django.http import HttpResponse
from django.template import loader

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from mistralai import Mistral

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from django.conf import settings
import os
from django.conf import settings
import re
from django.http import HttpResponseRedirect
from django.urls import reverse
import requests



@csrf_exempt
def analysis_view(request):
    current_user = request.user
    context = {
        'user': current_user,
    }
    if not request.user.is_authenticated: #if the user is not authenticated
        return HttpResponseRedirect(reverse("login_page"))
    else:
        if request.method == 'POST':
            user_input = request.POST.get('message', '')
            print(user_input)
            #user_input = request.POST.get('user_input')
            openai_response = get_mistral_response(user_input)
            return JsonResponse({'message': openai_response})
        return render(request, 'analysis.html', context)