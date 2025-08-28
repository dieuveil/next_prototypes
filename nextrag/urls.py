from django.urls import path
from . import views

urlpatterns = [
    #path("", views.index, name="index"),
    path("", views.rag_view, name='rag_view'),

]