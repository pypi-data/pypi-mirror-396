import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from pydantic import ValidationError
from transformers import T5ForConditionalGeneration, T5Tokenizer

from agent_3d_summarize.helpers import json_to_prompt
from djangoldp_ai_agents.helpers import ObjectList

model_name = "./agent_3d_summarize/model"
tokenizer = T5Tokenizer.from_pretrained(model_name, revision="main")
model = T5ForConditionalGeneration.from_pretrained(model_name, revision="main")


@method_decorator(csrf_exempt, name="dispatch")
class SummarizeView(View):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
            object_list = ObjectList(items=payload.get("items", []))
        except (json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)

        input_text = json_to_prompt(object_list.items)
        inputs = tokenizer(
            input_text, return_tensors="pt", max_length=512, truncation=True
        )

        outputs = model.generate(**inputs, max_length=200, num_beams=4, do_sample=False)
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return JsonResponse({"summary": summary})
