import json
import os

import numpy as np
import onnxruntime as rt
import pandas as pd
from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


# --- Feature engineering functions (copied from make_model.py) ---
def build_company(company: dict) -> str:
    return "\n".join(
        [
            f"sector: {company.get('sector', '')}",
            f"preferred_use: {', '.join(company.get('preferred_use', []))}",
            f"preferred_formats: {', '.join(company.get('preferred_formats', []))}",
            f"region_focus: {', '.join(company.get('region_focus', []))}",
            f"keywords: {', '.join(company.get('keywords', []))}",
            "projects: "
            + " | ".join(
                [
                    f"{p['type']} ({', '.join(p['object_needs'])})"
                    for p in company.get("current_projects", [])
                ]
            ),
            "history: "
            + " | ".join(
                [
                    o["object_id"]
                    for o in company.get("history", {}).get("liked_objects", [])
                    + company.get("history", {}).get("downloads", [])
                ]
            ),
        ]
    )


def build_object(obj: dict):
    return "\n".join(
        [
            f"id: {obj.get('@id', '')}",
            f"title: {obj.get('tc:title', '')}",
            f"description: {obj.get('description', '')}",
            f"country: {obj.get('country', '')}",
            f"time_period: {obj.get('time_period', '')}",
            f"format: {obj.get('format', '')}",
            f"polygons: {obj.get('polygons', '')}",
            f"texture_format: {obj.get('texture_formats', '')}",
        ]
    )


# Load data and model globally to avoid reloading on each request
MODEL_DIR = os.path.join(
    settings.BASE_DIR, "agent_recommendation", "model"
)  # Assuming BASE_DIR is the project root
COMPANIES_PATH = os.path.join(MODEL_DIR, "companies.json")
OBJECTS_PATH = os.path.join(MODEL_DIR, "3Dobjects.jsonld")
MODEL_PATH = os.path.join(MODEL_DIR, "recommender_model.onnx")

companies_data = {c["@id"]: c for c in json.load(open(COMPANIES_PATH))}
objects_data = {
    obj["@id"]: obj for obj in json.load(open(OBJECTS_PATH))["ldp:contains"]
}
onnx_session = rt.InferenceSession(MODEL_PATH)
input_name = onnx_session.get_inputs()[0].name
output_name = onnx_session.get_outputs()[0].name


@method_decorator(csrf_exempt, name="dispatch")
class RecommendView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            company_id = data.get("company_id")
            object_ids = data.get("object_ids", [])

            if not company_id or not object_ids:
                return JsonResponse(
                    {"error": "company_id and object_ids are required"},
                    status=400,
                )

            company = companies_data.get(company_id)
            if not company:
                return JsonResponse({"error": "Company not found"}, status=404)

            company_feature = build_company(company)

            recommendations = []
            for obj_id in object_ids:
                obj = objects_data.get(obj_id)
                if not obj:
                    continue

                object_feature = build_object(obj)
                text_feature = company_feature + "\n\n" + object_feature

                input_data = [text_feature]
                input_feed = {input_name: np.array(input_data).reshape(-1, 1)}

                results = onnx_session.run([output_name], input_feed)

                prediction = results[0][0][0]

                if prediction == 1:
                    recommendations.append(obj_id)

            return JsonResponse({"recommendations": recommendations}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
