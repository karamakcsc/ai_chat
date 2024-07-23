# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
import uuid
import cohere
import requests
import json
from frappe.model.document import Document
from ai_chat.api import validate_json_text

cohere_api_key = "pBnwCbT9CDGKcHw50gDTd5AJxMUqFrlY6q6FZ05o"
co = cohere.Client(cohere_api_key, client_name="frappe-dev")
def base_request_cohere_data():
    url = 'https://api.cohere.ai/v1/chat'
    headers = {
        "Authorization": "Bearer pBnwCbT9CDGKcHw50gDTd5AJxMUqFrlY6q6FZ05o",
        "Content-Type": "application/json"
    }
    return url, headers
class GenerateItemsDescription(Document):
	# def validate(self):
	# 	count_items(self)

	@frappe.whitelist()
	def check_item_description(self):
		try:
			self.items_table.clear()
			item_desc = frappe.db.sql(""" SELECT name, item_name, description FROM `tabItem` WHERE item_name = description LIMIT 10 """, as_dict = True)
			print(item_desc)
			items_list = []
			if item_desc:
				for item in item_desc:
					dict_items = {
						"item_code": item.name,
						"item_name": item.item_name,
						"description": item.description
					}
					items_list.append(dict_items)
				print(items_list)
				system_message = f"Based on this items '{items_list}', I want you to give me a description for this list of items as a JSON format with keys 'item_code', 'item_name', and 'description', don't change the 'item_code' and 'item_name'."
				cid = str(uuid.uuid4())
				stream = co.chat_stream(message=system_message, conversation_id=cid, model='command-r-plus', connectors=[], temperature=0.3)
				output = ''
				for idx, response in enumerate(stream):
					if response.event_type == "text-generation":
						output += response.text
					if idx == 0:
						desc = [" " + output]
					else:
						desc[-1] = output
				# frappe.throw(str(output))
				json_text = (output.split("```json"))[1].split("```")[0]
				print(json_text)
				json_data = validate_json_text(json_text)
				print(json_data)
				for data in json_data:
					self.append('items_table', {
						"item_code": data['item_code'],
						"item_name": data['item_name'],
						"item_description": data['description'],
					})
				self.save()
			else:
				frappe.msgprint("Error: No items retrieved.")
			return "Success"
		except Exception as e:
			return f"Exception Check Item Description Error: {str(e)}"
		
	@frappe.whitelist()
	def submit_item_description(self):
		child_table_data = {
            "items": [row.as_dict() for row in self.items_table],
        }
		child_table_items = child_table_data['items']
		for items in child_table_items:
			item_code = items['item_code']
			description = items['item_description']
			frappe.db.set_value("Item", item_code, "description", description)
		print(str(child_table_items))

# @frappe.whitelist()
# def count_items(self):
# 	count_items = frappe.db.sql(""" SELECT COUNT(item_code) FROM `tabItem` WHERE item_name = description """)
# 	# frappe.throw(self.name)
# 	frappe.db.set_value("Generate Items Description", self.name, "item_count", count_items)