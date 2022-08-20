from django.urls import path

from . import views

app_name = "pages"
urlpatterns = [
    path('', views.PageList.as_view(), name="list"),    
    path('new', views.NewPage.as_view(), name="new"),
    path('<str:slug>/edit', views.EditPage.as_view(), name="edit"),
    path('<str:slug>', views.ShowPage.as_view(), name="detail"),
]
