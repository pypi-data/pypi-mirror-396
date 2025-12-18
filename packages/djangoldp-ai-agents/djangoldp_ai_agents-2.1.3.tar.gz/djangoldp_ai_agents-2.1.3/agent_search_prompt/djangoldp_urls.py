from django.urls import path

from .views import SearchPromptView

urlpatterns = [
    path("search-prompt", SearchPromptView.as_view(), name="search-prompt"),
]
