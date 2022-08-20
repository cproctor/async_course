from django.urls import path

from . import views

app_name = "profiles"
urlpatterns = [
    path('<str:username>/edit', views.EditProfile.as_view(), name="edit"),
    path('<str:username>/grades', views.ShowGrades.as_view(), name="grades"),
    path('<str:username>', views.ShowProfile.as_view(), name="detail"),
]

