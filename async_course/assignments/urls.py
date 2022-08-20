from django.urls import path

from . import views

app_name = "assignments"
urlpatterns = [
    path('', views.AssignmentList.as_view(), name="list"),    
    path('new', views.NewAssignment.as_view(), name="new"),
    path('<str:slug>/edit', views.EditAssignment.as_view(), name="edit"),
    path('<str:slug>', views.ShowAssignment.as_view(), name="detail"),
]

