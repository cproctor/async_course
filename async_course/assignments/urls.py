from django.urls import path

from assignments import views
from reviews import views as review_views

app_name = "assignments"
urlpatterns = [
    path('', views.ListAssignments.as_view(), name="list"),    
    path('new', views.NewAssignment.as_view(), name="new"),
    path('<str:slug>/edit', views.EditAssignment.as_view(), name="edit"),
    path('<str:slug>/roster', views.ShowAssignmentRoster.as_view(), name="roster"),
    path('<str:slug>/<str:username>', views.ShowAssignmentSubmissions.as_view(), 
            name="submissions"),
    path('<str:slug>/<str:username>/v<int:version>/reviews', 
            review_views.NewReview.as_view(), name="new_review"),
    path('<str:slug>/<str:username>/v<int:version>/reviews/<int:review_id>', 
            review_views.EditReview.as_view(), name="edit_review"),
    path('<str:slug>/<str:username>/v<int:version>', views.DownloadSubmission.as_view(), 
            name="download_submission"),
    path('<str:slug>', views.ShowAssignment.as_view(), name="detail"),
]

