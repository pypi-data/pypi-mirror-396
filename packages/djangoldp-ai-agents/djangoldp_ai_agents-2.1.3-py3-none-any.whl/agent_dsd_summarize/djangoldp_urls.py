from django.urls import path

from agent_dsd_summarize.views import (CommentSummarizeView,
                                       ConsultationSummarizeView,
                                       PropositionSummarizeView)

urlpatterns = [
    path("summarize/consultation/", ConsultationSummarizeView.as_view(), name="summarize_consultation"),
    path("summarize/proposition/", PropositionSummarizeView.as_view(), name="summarize_proposition"),
    path("summarize/comment/", CommentSummarizeView.as_view(), name="summarize_comment"),
]
