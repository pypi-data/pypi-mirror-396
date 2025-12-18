import json
from functools import partial

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from pydantic import ValidationError

from agent_dsd_summarize.helpers import (format_for_prompt,
                                         get_mistral_summary, json_to_prompt)
from djangoldp_ai_agents.helpers import ObjectList


@method_decorator(csrf_exempt, name="dispatch")
class BaseSummarizeView(View):
    system_prompt = ""
    formatter = None
    context_key = None
    context_formatter = None
    items_title = ""

    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
            object_list = ObjectList(items=payload.get("items", []))
            context_data = payload.get(self.context_key) if self.context_key else None
        except (json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)

        context_details = ""
        if context_data and self.context_formatter:
            context_details = (
                f"Les {self.items_title} suivantes concernent les {self.items_title} faits dans le cadre de:\n"
                f"{self.context_formatter(context_data)}\n\n"
                f"--- {self.items_title.upper()} ---\n"
            )

        items_text = json_to_prompt(object_list.items, formatter=self.formatter)
        input_text = context_details + items_text

        summary = get_mistral_summary(input_text, self.system_prompt)

        if summary:
            return JsonResponse({"summary": summary})
        else:
            return JsonResponse(
                {"error": "Failed to get summary from Mistral AI."}, status=500
            )


class ConsultationSummarizeView(BaseSummarizeView):
    """
    Summarize a list of consultations.
    Example payload:
    {
        "items": [
            {
                "name": "Consultation 1",
                "description": "Description 1",
                "organizer": {"name": "Organizing Body 1"}
            }
        ]
    }
    """

    system_prompt = (
        "Vous êtes un expert en résumé de textes. Votre rôle est de synthétiser les "
        "principales préoccupations à partir de la liste de consultations fournie. Chaque "
        "consultation comprend un titre, une description, une catégorie et l'organisme "
        "organisateur. Fournissez un résumé très court en une phrase en français qui "
        "met en évidence les principaux problèmes soulevés. "
        "Le texte doit être rédigé sans markdown ni mise en forme."
    )
    formatter = partial(
        format_for_prompt,
        fields=[
            ("Title", "name"),
            ("Description", "description"),
            ("Organizing Body", "organizer"),
        ],
    )


class PropositionSummarizeView(BaseSummarizeView):
    """
    Summarize a list of propositions within the context of a consultation.
    Example payload:
    {
        "consultation": {
            "name": "Consultation 1",
            "description": "Description 1",
            "category": "Category 1",
            "organizer": {"name": "Organizing Body 1"}
        },
        "items": [
            {
                "name": "Proposition 1",
                "description": "Description 1",
                "author": "Author 1",
                "date": "Date 1"
            }
        ]
    }
    """

    system_prompt = (
        "Vous êtes un expert en résumé de textes. Votre rôle est de synthétiser les "
        "principales idées de la liste de propositions fournie, en tenant compte du contexte de la consultation. "
        "Chaque proposition a un titre, une description, un auteur et une date. "
        "Fournissez un résumé court et factuel en français qui met en évidence les points clés soulevés dans les propositions. "
        "Le texte doit être rédigé sans markdown ni mise en forme."
    )
    formatter = partial(
        format_for_prompt,
        fields=[
            ("Title", "name"),
            ("Description", "description"),
            ("Proposal State", "proposalState"),
            ("Participant count", "participantCount"),
            ("Vote count", "voteCount"),
            ("Creator", "creator"),
        ],
    )
    context_key = "consultation"
    context_formatter = partial(
        format_for_prompt,
        fields=[
            ("Title", "name"),
            ("Description", "description"),
            ("Organizing Body", "organizer"),
        ],
    )
    items_title = "propositions"


class CommentSummarizeView(BaseSummarizeView):
    """
    Summarize a list of comments within the context of a proposition.
    Example payload:
    {
        "proposition": {
            "name": "Proposition 1",
            "description": "Description 1",
            "author": "Author 1",
            "date": "Date 1"
        },
        "items": [
            {
                "name": "Comment 1",
                "description": "Description 1",
                "author": "Author 1",
                "date": "Date 1"
            }
        ]
    }
    """

    system_prompt = (
        "Vous êtes un expert en résumé de textes. Votre rôle est de synthétiser les "
        "principaux points d'une liste de commentaires, en tenant compte du contexte de la proposition. "
        "Le résumé doit commencer par les points positifs, puis les points neutres, et enfin les points négatifs. "
        "Restez factuel et concis. Le texte doit être rédigé sans markdown ni mise en forme."
    )
    formatter = partial(
        format_for_prompt,
        fields=[
            ("Title", "name"),
            ("Description", "description"),
            ("Author", "author"),
            ("Date", "date"),
        ],
    )
    context_key = "proposition"
    context_formatter = partial(
        format_for_prompt,
        fields=[
            ("Title", "name"),
            ("Description", "description"),
            ("Author", "author"),
            ("Date", "date"),
        ],
    )
    items_title = "commentaires"
