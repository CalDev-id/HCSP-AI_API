from pdf2image import convert_from_bytes
from io import BytesIO
import base64
import requests
import json
import os

API_URL = "https://telkom-ai-dag.api.apilogy.id/LargeMultimodalModel/0.0.2/lmm/chat/completions"

with open("config/secrets/apilogy_LMM.txt", "r") as f:
            os.environ["APILOGY_API_KEY"] = f.read().strip()

api_key = os.environ.get("APILOGY_API_KEY")

async def ocr_pdf_apilogy(upload_file) -> list[dict]:
    pdf_bytes = await upload_file.read()

    images = convert_from_bytes(pdf_bytes, dpi=300)

    all_pages = []
    for i, img in enumerate(images, start=1):
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        base64_image = base64.b64encode(img_bytes.read()).decode("utf-8")

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Extract and return only the raw text from the document image, without any summary, interpretation, or explanation. Do not add extra words, just return the plain text as it appears in the document. Page {i}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 5000,
            "temperature": 0,
            "stream": False
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": api_key
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        try:
            resp_json = response.json()
            content = resp_json["choices"][0]["message"]["content"]
        except Exception:
            content = f"Error: {response.text}"

        all_pages.append({
            "page": i,
            "content": content.strip()
        })

    return all_pages
