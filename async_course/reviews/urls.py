from django.urls import path

from . import views

app_name = "reviews"
urlpatterns = [
    path('<int:pk>/edit', views.EditReview.as_view(), name="edit"),
    path('<int:pk>/delete', views.DeleteReview.as_view(), name="delete"),
]

