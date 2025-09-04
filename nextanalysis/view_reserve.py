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
from langchain.prompts import PromptTemplate

from langchain.sql_database import SQLDatabase
from langchain_mistralai.chat_models import ChatMistralAI
import re



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
    response_text = ""
    sql_query = ""
    user_question = ""

    if request.method == 'POST':
        user_question = request.POST.get("question")

        # 🔐 API key and DB connection
        mistral_api_key = "EgUOnMcphwYW8I167T3A4J0keFUtOdIW"
        mysql_uri = "mysql+pymysql://root:0801@localhost:3306/bank"

        try:
            # 🔌 Connect to MySQL
            db = SQLDatabase.from_uri(mysql_uri)

            # 🤖 Load Mistral model
            llm = ChatMistralAI(
                api_key=mistral_api_key,
                model="mistral-small-latest",
                temperature=0.3,
            )

            # 📜 Define custom prompt to avoid Markdown
            custom_prompt = PromptTemplate.from_template(
                "Étant donné une question, génère une requête MySQL syntaxiquement correcte pour y répondre. "
                "Retourne UNIQUEMENT la requête SQL, sans aucun formatage Markdown ou ```sql. "
                "Question : {input}"
            )

            # 🔗 Build SQL chain
            chain = SQLDatabaseChain.from_llm(
                llm,
                db,
                verbose=True,
                return_intermediate_steps=True,
                prompt=custom_prompt
            )

            result = chain(user_question)

            intermediate_steps = result.get('intermediate_steps', [])
            raw_sql = ""

            # Extract SQL string depending on the format
            if intermediate_steps:
                first_step = intermediate_steps[0]

                if isinstance(first_step, dict):
                    # Get the SQL string from the dictionary (common structure)
                    raw_sql = first_step.get('sql_cmd', '')
                elif isinstance(first_step, str):
                    # It's already a string
                    raw_sql = first_step

                # Clean the SQL
                sql_query = re.sub(r"```(?:sql)?\n?", "", raw_sql).replace("```", "").strip()
            else:
                sql_query = ""

            print("Raw SQL:", raw_sql)
            print("Response text:", response_text)
            response_text = result.get('result', 'Aucune réponse')

        except Exception as e:
            response_text = f"Voici Erreur : {e}"

    return render(request, 'ask_sql.html', {
        'question': user_question,
        'response': response_text,
        'sql_query': sql_query,
    })