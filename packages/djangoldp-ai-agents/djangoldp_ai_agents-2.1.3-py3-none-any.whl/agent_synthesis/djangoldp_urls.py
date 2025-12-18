from django.urls import path

from .views import SynthesisView

urlpatterns = [
    path("synthesis", SynthesisView.as_view(), name="synthesis"),
]
