from django.urls import path
from . import views

urlpatterns = [
    #path("", views.index, name="index"),
    #path("", views.analysis_view, name='analysis_view'),
    #path("ask_sql/", views.ask_sql, name='ask_sql'),
    path("", views.ask_sql, name='ask_sql'),

]