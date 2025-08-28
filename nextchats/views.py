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


API_KEY = "EgUOnMcphwYW8I167T3A4J0keFUtOdIW"
ENDPOINT = "https://api.mistral.ai/v1/chat/completions"  
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}


def get_openai_response(prompt):
    api_key = "EgUOnMcphwYW8I167T3A4J0keFUtOdIW"
    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)

    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    print(chat_response.choices[0].message.content)
    return chat_response.choices[0].message.content



def get_mistral_response(prompt):
    api_key = "EgUOnMcphwYW8I167T3A4J0keFUtOdIW"
    model = "mistral-small-latest"

    client = Mistral(api_key=api_key)

    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    print(chat_response.choices[0].message.content)
    return chat_response.choices[0].message.content



# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    template = loader.get_template('welcome.html')
    return HttpResponse(template.render())


@csrf_exempt
def chat_view(request):
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
            openai_response = get_openai_response(user_input)
            return JsonResponse({'message': openai_response})
        return render(request, 'chat.html', context)



# Define a view function for the login page
def login_page(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if a user with the provided username exists
        if not User.objects.filter(username=username).exists():
            # Display an error message if the username does not exist
            messages.error(request, 'Invalid Username')
            return redirect('/login/')
        
        # Authenticate the user with the provided username and password
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Invalid Password")
            return redirect('/login/')
        else:
            # Log in the user and redirect to the home page upon successful login
            login(request, user)
            return redirect('/chat')
    
    # Render the login page template (GET request)
    return render(request, 'login.html')



# Define a view function for the registration page
def register_page(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if a user with the provided username already exists
        user = User.objects.filter(username=username)
        
        if user.exists():
            # Display an information message if the username is taken
            messages.info(request, "Username already taken!")
            return redirect('/register/')
        
        # Create a new User object with the provided information
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        
        # Set the user's password and save the user object
        user.set_password(password)
        user.save()
        
        # Display an information message indicating successful account creation
        messages.info(request, "Account created Successfully!")
        return redirect('chat')
    
    # Render the registration page template (GET request)
    return render(request, 'register.html')



def user_logout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request) 
            messages.success(request, 'Logout Successful')
    return redirect('/')