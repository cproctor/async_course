from django.urls import path
from profiles import views

app_name = "profiles"
urlpatterns = [
    path('<str:username>/edit', views.EditProfile.as_view(), name="edit"),
    path('<str:username>/grades', views.ShowGrades.as_view(), name="grades"),
    path('<str:username>/password', views.ChangePassword.as_view(), name="password"),
    path('<str:username>', views.ShowProfile.as_view(), name="detail"),
]

