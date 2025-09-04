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

import pymysql


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
                return_intermediate_steps=False,  # Don't return intermediate steps
                prompt=custom_prompt
            )

            result = chain(user_question)

            # Extract the generated SQL query from the result
            sql_query = result.get('result', '')

            # Clean the SQL query (in case there is any extra formatting)
            sql_query = re.sub(r"```(?:sql)?\n?", "", sql_query).replace("```", "").strip()

            # Now, execute the SQL query using pymysql
            if sql_query:
                # Connect to MySQL using pymysql
                connection = pymysql.connect(
                    host='localhost',
                    user='root',
                    password='0801',
                    database='bank'
                )

                try:
                    with connection.cursor() as cursor:
                        # Execute the SQL query
                        cursor.execute(sql_query)

                        # If it's a SELECT query, fetch the results
                        if sql_query.strip().lower().startswith('select'):
                            result_set = cursor.fetchall()
                            response_text = result_set  # You could format this or display it as needed
                        else:
                            # If it's an UPDATE/INSERT/DELETE, we don't fetch data, just give feedback
                            connection.commit()
                            response_text = "La requête SQL a été exécutée avec succès."
                except Exception as e:
                    response_text = f"Erreur lors de l'exécution de la requête SQL : {e}"
                finally:
                    connection.close()

            else:
                response_text = "Aucune requête SQL générée."

        except Exception as e:
            response_text = f"Erreur lors de la génération de la requête SQL : {e}"

    return render(request, 'ask_sql.html', {
        'question': user_question,
        'response': response_text,
        'sql_query': sql_query,
    })