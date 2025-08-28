from django.http import HttpResponse
from django.template import loader

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
#from mistralai import Mistral
#from langchain_community.chat_models import ChatMistralAI
from langchain_mistralai.chat_models import ChatMistralAI

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


from django.shortcuts import render
from dotenv import load_dotenv
#from langchain.chains import SQLDatabaseChain
from langchain_experimental.sql import SQLDatabaseChain

from langchain.sql_database import SQLDatabase
from langchain_mistralai.chat_models import ChatMistralAI



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




def ask_sql(request):
     # Initialisation des variables qui seront envoyées au template
    response_text = ""
    sql_query = ""
    user_question = ""

    # Vérifie si le formulaire a été soumis en méthode POST
    if request.method == 'POST':
        # Récupère la question posée par l'utilisateur depuis le champ "question"
        user_question = request.POST.get("question")

        # Charge les variables d’environnement depuis le fichier .env
        mistral_api_key = "EgUOnMcphwYW8I167T3A4J0keFUtOdIW"
        mysql_uri = "mysql+pymysql://root:0801@localhost:3306/bank"

        try:
            # Connexion à la base de données MySQL via SQLAlchemy
            db = SQLDatabase.from_uri(mysql_uri)

            # Création du modèle LLM de Mistral via le wrapper LangChain
            llm = ChatMistralAI(
                api_key=mistral_api_key,
                model="mistral-small-latest",  # ou "mistral-medium-latest", selon ton abonnement
                temperature=0.3,  # plus bas = réponses plus déterministes
            )

            # Création de la chaîne LangChain SQL qui relie le LLM à la base SQL
            chain = SQLDatabaseChain.from_llm(
                llm,
                db,
                verbose=True,  # Affiche les étapes internes dans la console
                return_intermediate_steps=True  # Permet de récupérer la requête SQL générée
            )

            # Exécution de la chaîne avec la question utilisateur
            result = chain(user_question)
           
            # Récupère la réponse en langage naturel
            response_text = result.get('result', 'Aucune réponse')
            print(response_text)

            # Récupère la requête SQL générée par le LLM
            sql_query = result.get('intermediate_steps', [''])[0]
            print("and")
            print(sql_query)

        except Exception as e:
            # En cas d’erreur (ex : problème API, base de données, etc.)
            response_text = f"Voici Erreur : {e}"


    # Rendu du template HTML avec les données à afficher
    return render(request, 'ask_sql.html', {
        'question': user_question,
        'response': response_text,
        'sql_query': sql_query,
    })