# Copyright (c) 2024, jibreel abdeen and contributors
# For license information, please see license.txt
import frappe
import os
import json
import requests
from frappe.model.document import Document
persist_directory = '/home/ubuntu/frappe-bench/apps/ai_chat/ai_chat/ai_chat/doctype/chat/chroma/'
os.environ["OPENAI_API_KEY"] = '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'
API_TOKEN = "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"

model_id = "Helsinki-NLP/opus-mt-zh-en"
# "meta-llama/Meta-Llama-3-8B-Instruct" weak
# "meta-llama/Meta-Llama-3-8B" too large to load automatically
# "google/flan-t5-base"
# "meta-llama/Meta-Llama-3-8B-Instruct" not accurate

API_URL = "https://api-inference.huggingface.co/models/" + model_id
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}




class chat(Document):
	pass



@frappe.whitelist()
def get_ai_answer(request):
	data = query(request)
	print(data)
	return data


def query(question):
    payload = {
	"inputs": question,
}
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))




