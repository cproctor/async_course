from django.urls import path

from . import views

app_name = "posts"
urlpatterns = [
    path('', views.PostList.as_view(), name="list"),    
    path('new', views.NewPost.as_view(), name="new"),
    path('<int:pk>/edit', views.EditPost.as_view(), name="edit"),
    path('<int:pk>/reply', views.ReplyToPost.as_view(), name="reply"),
    path('<int:pk>/upvote', views.UpvotePost.as_view(), name="upvote"),
    path('<int:pk>', views.ShowPost.as_view(), name="detail"),
]
