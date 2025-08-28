from django.urls import path
from . import views

urlpatterns = [
    #path("", views.index, name="index"),
    path("", views.analysis_view, name='analysis_view'),

]