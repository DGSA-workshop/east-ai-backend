import os
import json
import boto3
from fastapi import APIRouter
from utils.aws import translate
from utils.common import get_int, get_str


class Bedrock:
    def __init__(self):
        region = os.environ.get("AWS_DEFAULT_REGION", "us-west-2")
        self.bedrock = boto3.client("bedrock-runtime", region_name=region)
        self.router = APIRouter()
        self.router.add_api_route(
            "/api/bedrock-product-design", self.bedrock_product_design, methods=["POST"]
        )

    def bedrock_product_design(self, item: dict):
        prompt_res = translate(get_str(item, "prompt", None))
        prompt = "3D product render, {p}, finely detailed, purism, ue 5, a computer rendering, minimalism, octane render, 4k".format(
            p=prompt_res
        )

        negative_prompt = get_str(item, "negative_prompt")

        if negative_prompt:
            negative_prompt = translate(negative_prompt)

        steps = get_int(item, "steps", 30)
        # item["seed"] = int(item["seed"]) or -1
        height = get_int(item, "height", 512)
        width = get_int(item, "width", 512)
        count = get_int(item, "count", 1)
        style_preset = get_str(item, "style_preset", "3d-model")
        request = json.dumps(
            {
                "text_prompts": (
                    [
                        {"text": prompt, "weight": 1.0},
                        {"text": negative_prompt, "weight": -1.0},
                    ]
                ),
                "cfg_scale": 10,
                # "seed": -1,
                "steps": steps,
                "style_preset": style_preset,
                "width": width,
                "height": height,
                "count": count,
            }
        )
        modelId = "stability.stable-diffusion-xl"
        print(request)
        response = self.bedrock.invoke_model(body=request, modelId=modelId)
        response_body = json.loads(response.get("body").read())
        print(len(response_body["artifacts"]))
        return {"images": [response_body["artifacts"][0].get("base64")]}


bedrock_router = Bedrock().router