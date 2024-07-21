# Copyright (c) 2024, jibreel abdeen and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
# import re

class jsontexttojson(Document):
	pass

history = []

@frappe.whitelist()   
def clear_chat():
    history.clear()
    return history


    
@frappe.whitelist()   
def generate_response(message):
	# Print the JSON objects
	# print(f"the span is :  {json_textstart.end()} to {json_textend.start()}")
	json_text = (message.split("```json"))[1].split("```")[0]
	# print(json_text)
	# Parse the JSON text into JSON objects
	try:
		json_objects = json.loads(json_text)
		reply = json_objects
	except:
		reply = f"Error"
	# print(json_objects)
	return reply






# Find the positions of the start and end notations


