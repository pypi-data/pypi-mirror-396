import json
import os

import pandas as pd
from django.core.management.base import BaseCommand
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import StringTensorType
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


class Command(BaseCommand):
    help = "Trains and exports the recommendation model."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting model training..."))

        base_path = os.path.join(os.path.dirname(__file__), "..", "..")

        # --- Loading data ---
        companies_path = os.path.join(base_path, "companies.json")
        objects_path = os.path.join(base_path, "3Dobjects.jsonld")
        interactions_path = os.path.join(base_path, "interactions.csv")

        companies = {c["@id"]: c for c in json.load(open(companies_path))}
        objects = {
            obj["@id"]: obj
            for obj in json.load(open(objects_path))["ldp:contains"]
        }
        interactions = pd.read_csv(interactions_path)

        # --- Feature engineering ---
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

        def build_company_feature(company_id: str) -> str:
            company = companies.get(company_id)
            return build_company(company)

        def build_object_feature(object_id: str) -> str:
            obj = objects.get(object_id)
            if not obj:
                return ""
            return build_object(obj)

        def build_feature(row):
            return (
                build_company_feature(row["company_id"])
                + "\n\n"
                + build_object_feature(row["object_id"])
            )

        # --- Training ---
        interactions["text_features"] = interactions.apply(build_feature, axis=1)
        x_train, x_test, y_train, y_test = train_test_split(
            interactions["text_features"],
            interactions["label"],
            test_size=0.2,
            random_state=42,
        )
        pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(max_features=5000)),
                ("clf", RandomForestClassifier(n_estimators=100, class_weight="balanced")),
            ]
        )
        pipeline.fit(x_train, y_train)

        # --- Export model ---
        model_output_path = os.path.join(base_path, "model/recommender_model.onnx")
        onnx_model = convert_sklearn(
            pipeline,
            initial_types=[("input", StringTensorType([None, 1]))],
            options={id(pipeline): {"zipmap": False}},
        )
        with open(model_output_path, "wb") as f:
            f.write(onnx_model.SerializeToString())

        self.stdout.write(
            self.style.SUCCESS(f"Model successfully exported to {model_output_path}")
        )

        # --- Evaluate the model ---
        y_pred = pipeline.predict(x_test)
        self.stdout.write("Classification Report:")
        self.stdout.write(str(classification_report(y_test, y_pred)))

        self.stdout.write(self.style.SUCCESS("Model training completed."))
