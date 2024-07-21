# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
import uuid
import cohere
from frappe.model.document import Document
from ai_chat.api import validate_json_text

cohere_api_key = "lc9DVbwzyvxgzwbWXZgcmtVxaJk7IyrmMTX2RV5P"
co = cohere.Client(cohere_api_key, client_name="frappe-dev")

class GenerateItemsDescription(Document):
	@frappe.whitelist()
	def check_item_description(self):
		try:
			self.items_table.clear()
			item_desc = frappe.get_all("Item", filters={}, fields=["name", "item_name", "description"])
			item_list = []
			if item_desc:
				for item in item_desc:
					if item.item_name == item.description:
						dict_items = {
							"item_code" : item.name,
							"item_name" : item.item_name,
							"description" : item.description
							}
						item_list.append(dict_items)
					else:
						frappe.msgprint("All Items are good.")
			else:
				frappe.msgprint("Error No Items Retrieved.")
			system_message = f"Based on the items '{item_list}' i want you to give me a description for each item as a json format with keys item_code, item_name and description in both Arabic and Engilish Languages"
			cid = str(uuid.uuid4())
			stream = co.chat_stream(message=system_message, conversation_id=cid, model='command-r-plus', connectors=[], temperature=0.3)
			output = ''
			# for idx, response in enumerate(stream):
			# 	if response.event_type == "text-generation":
			# 		output += response.text
			# 	if idx == 0:
			# 		desc = [" " + output]
			# 	else:
			# 		desc[-1] = output
			# print(str(output))
			frappe.throw(str(stream))
		# 	json_text = (desc.split("```json"))[1].split("```")[0]
		# 	json_data = validate_json_text(json_text)
		# 	print(str(json_data))
		# 	for items in json_data:
		# 		item_code = items['item_code']
		# 		item_name = items['item_name']
		# 		description = items['description']
		# 		self.append('items_table', {
		# 					"item_code" : item_code,
		# 					"item_name" : item_name,
		# 					"description" : description
		# 				})
		# 		# frappe.db.set_value('Item', item_code, 'description', description)
			return "Success"
		except Exception as e:
			return f"Exception Check Item Description Error: {str(e)}"