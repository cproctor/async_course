from django.urls import path

from . import views

app_name = "pubref"
urlpatterns = [
    path('', views.PublicationList.as_view(), name="list"),    
    path('add', views.AddPublications.as_view(), name="add"),
    path('<str:slug>/edit', views.EditPublication.as_view(), name="edit"),
    path('<str:slug>/delete', views.DeletePublication.as_view(), name="delete"),
    path('<str:slug>', views.ShowPublication.as_view(), name="detail"),
]

