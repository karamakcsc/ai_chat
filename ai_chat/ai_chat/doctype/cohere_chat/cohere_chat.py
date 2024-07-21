# Copyright (c) 2024, jibreel abdeen and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
# from transformers import pipeline
import frappe
import cohere
import os
# import re
import uuid
import json
import requests
from frappe import utils
# import secrets
from ai_chat.api import create_purchase_order
from ai_chat.api import (base_request_data ,
                         validate_json_text , 
                         process_search_items ,
                         validate_item_description ,
                         search_in_commonly_known_names , 
                         qty_check,
                         item_alternative)


class cohere_chat(Document):
    def on_submit(self):
        create_purchase_order(str(self.company), str(self.supplier), str(self.history))
    
    def validate(self):
        items_availability_check(self)

cohere_api_key = "lc9DVbwzyvxgzwbWXZgcmtVxaJk7IyrmMTX2RV5P"
co = cohere.Client(cohere_api_key, client_name="frappe-dev")

def trigger_example(example):
    chat, updated_history = generate_response(example)
    return chat, updated_history

history = []
cohere_message_for_user = []
desc = []

@frappe.whitelist()        
def generate_response(user_message, cid, token):

    if not token:
        raise frappe.msgprint({
                "title": "Alert",
                "message": "Error loading. not authorized, make sure to have valid API token",
                "indicator": "red"})
        # frappe.msgprint("history array initiated")
    if cid == "" or None:    
        cid = str(uuid.uuid4())
    if len(history) == 0:
        system_message = 'Extract the retailer shop order from message below, Analyze the data and understand the retailer shop order accurately extract the features of "item", "descirption", float value ("qty"), "commonly known as", "category", subcategory", "variance", "basic measuring unit", "package measuring unit" and "brand". give output in json format and include the following metrics in each response, session id , session duration elapsed time, tokens per input, tokens per output, total session input and output tokens and response time, user-message language, supplier and a list of items in the order.  the message is '
        user_message = system_message + user_message
    
    
    print(f"cid: {cid} prompt:{ user_message}")
    
    history.append(user_message)
    
    stream = co.chat_stream(message=user_message, conversation_id=cid, model='command-r-plus', connectors=[], temperature=0.3)
    
    output = ""
    
    for idx, response in enumerate(stream):
        if response.event_type == "text-generation":
            output += response.text
        if idx == 0:
            history.append(" " + output)
        else:
            history[-1] = output
        chat = [
            (history[i].strip(), history[i + 1].strip())
            for i in range(0, len(history) - 1, 2)
        ] 
        yield chat, history, cid
        
    return chat, history, cid
    
@frappe.whitelist()   
def clear_chat(cid, token):
    history.clear()
    chat = []
    if not token:
        raise frappe.msgprint({
            "title": "Alert",
            "message": "Error loading. not authorized, make sure to have valid API token",
            "indicator": "red"})
    if cid == "" or None:    
        cid = str(uuid.uuid4())
    return chat, history, cid


examples = [
    "What are 8 good questions to get to know a stranger?",
    "Create a list of 10 unusual excuses people might use to get out of a work meeting",
]




@frappe.whitelist()   
def get_json_text(message):
	# Print the JSON objects
	# print(f"the span is :  {json_textstart.end()} to {json_textend.start()}")
    try:
        json_text = (message.split("```json"))[1].split("```")[0]
    # print(json_text)
    except:
        json_text= ""
	
    return json_text



      
@frappe.whitelist()
def items_availability_check(self):
        # self = frappe.get_doc('cohere_chat' , name )
        try:
            self.available_items_and_qty.clear()
            self.unavailable_qty.clear()
            self.unavailable_item.clear()
            # if len(history) != 0:
            json_text = self.history
            json_data = validate_json_text(json_text)
            order = json_data['order']
            if order:
                for items in list(order):
                    item_code_po = ''
                    item_code = items['item']
                    warehouse = 'Stores - KCSCD'
                    json_qty = items['qty']
                    commonly_known_as = items['commonly_known_as']
                    item_code_psi= process_search_items(item_code)
                    if item_code_psi:
                            item_code_po = item_code_psi
                            # frappe.throw(str())
                    else:
                        item_code_description = validate_item_description(item_code)
                        if item_code_description:
                            item_code_po = item_code_description
                        else:
                            item_code_search_in_commonly_known_names = search_in_commonly_known_names(item_code, commonly_known_as)
                            if  item_code_search_in_commonly_known_names:
                                item_code_po = item_code_search_in_commonly_known_names
                            else:
                                item_code_search_in_commonly_known= search_in_commonly_known_names(commonly_known_as, item_code)
                                if item_code_search_in_commonly_known:
                                    item_code_po = item_code_search_in_commonly_known
                    
                    unavailable_item = item_code
                    if item_code_po:
                        item_name = frappe.db.sql(f""" SELECT item_name FROM `tabItem` WHERE item_code = '{item_code_po}' """)
                    qty =  qty_check(json_qty, item_code_po, warehouse)
                    unavailable_qty = json_qty
                    
                    if item_code_po and qty:
                        self.append('available_items_and_qty', {
                            "item_code" : item_code_po,
                            "item_name" : item_name,
                            "qty" : qty,
                        })
                    if item_code_po and not qty:
                        actual_qty = frappe.db.sql(f""" SELECT actual_qty FROM `tabBin` WHERE item_code = '{item_code_po}' AND warehouse = '{warehouse}' """, as_dict = True)
                        actual_qty = actual_qty[0]['actual_qty'] if actual_qty else 0
                        alternative_item_list = item_alternative(item_code)
                        alt_code = ''
                        highest_alternative_qty = 0
                        alternative_item_name = ''
                        alternative_code = ''
                        # frappe.throw(str(alternative_item_list))
                        if alternative_item_list:
                        
                            # if alternative_item_list:
                            for alt_code in alternative_item_list:
                                alt_qty = qty_check(json_qty, alt_code, warehouse)
                                # frappe.throw(str(alt_qty))
                            # if alt_qty > highest_alternative_qty:
                                highest_alternative_qty = alt_qty
                                alternative_code = alt_code if alt_code else ''
                        alternative_item_name = frappe.db.sql(f"""SELECT item_name FROM `tabItem` WHERE item_code = '{alt_code}' """, as_dict=True)
                        alternative_item_name = alternative_item_name[0]['item_name'] if alternative_item_name else ''
                                # frappe.throw(str(alt_code))
                        self.append('unavailable_qty', {
                            "item_code" : item_code_po,
                            "item_name" : item_name,
                            "request_qty" : unavailable_qty,
                            "available_qty" : actual_qty,
                            "alternative_code" : alternative_code,
                            "alternative_name" : alternative_item_name,
                            "alternative_qty" : highest_alternative_qty,
                        })
                    if not item_code_po:
                        self.append('unavailable_item', {
                            "item" : unavailable_item,
                        })
            return "Success"
            # else:
            #     frappe.throw("Please generate a response before saving.")
        except Exception as e:
            return f"Exception Items Availability Check Error: {str(e)}"

            
@frappe.whitelist()
def analyze_child_table_data(docname, token):
    try:
        if not token:
            raise frappe.ValidationError("Error loading. not authorized, make sure to have valid API token")

        doc = frappe.get_doc('cohere_chat', docname)

        child_table_data = {
            "available_items_and_qty": [row.as_dict() for row in doc.available_items_and_qty],
            "unavailable_qty": [row.as_dict() for row in doc.unavailable_qty],
            "unavailable_item": [row.as_dict() for row in doc.unavailable_item]
        }
        json_text = doc.history
        json_data = validate_json_text(json_text)
        user_lang = json_data['user_message_language']
        # frappe.throw(str(user_lang))
        cohere_message_for_user = []
        system_message = f"Based on the Customer reaching out and my items in stock '{child_table_data}' generate a response in '{user_lang}' language for the customer to show him the availability of the items in stock"

        cid = str(uuid.uuid4())
        stream = co.chat_stream(message=system_message, conversation_id=cid, model='command-r-plus', connectors=[], temperature=0.3)
        output = ''

        for idx, response in enumerate(stream):
            if response.event_type == "text-generation":
                output += response.text
            if idx == 0:
                cohere_message_for_user.append(" " + output)
            else:
                cohere_message_for_user[-1] = output

        chat = [
            (cohere_message_for_user[i].strip(), cohere_message_for_user[i + 1].strip())
            for i in range(0, len(cohere_message_for_user) - 1, 2)
        ]

        # Uncomment the following lines if you need to use them
        # chat = generate_response(user_message, cid, token)
        # cohere_message_for_user = " ".join([response[1] for response in chat])
        # doc.cohere_message_for_user = cohere_message_for_user
        # doc.save()
        
        return cohere_message_for_user

    except Exception as e:
        frappe.msgprint(f"Error occurred at line {e.__traceback__.tb_lineno}")
        return f"Exception Analyze Child Table Data Error: {str(e)}"

# @frappe.whitelist()
# def check_item_description():
#     try:
#         # self.items_table.clear()
#         item_desc = frappe.get_all("Item", filters={}, fields=["name", "item_name", "description"])
#         item_list = []
#         if item_desc:
#             for item in item_desc:
#                 if item.item_name == item.description:
#                     dict_items = {
#                         "item_code" : item.name,
#                         "item_name" : item.item_name,
#                         "description" : item.description
#                         }
#                     item_list.append(dict_items)
#                 else:
#                     frappe.msgprint("All Items are good.")
#         else:
#             frappe.msgprint("Error No Items Retrieved.")
#         system_message = f"Based on the items '{item_list}' i want you to give me a description for each item as a json format with keys item_code, item_name and description in both Arabic and Engilish Languages"
#         cid = str(uuid.uuid4())
#         stream = co.chat_stream(message=system_message, conversation_id=cid, model='command-r-plus', connectors=[], temperature=0.3)
#         output = ''
#         for idx, response in enumerate(stream):
#             if response.event_type == "text-generation":
#                 output += response.text
#             if idx == 0:
#                 desc = [" " + output]
#             else:
#                 desc[-1] = output
#         # print(str(output))
#         frappe.throw(str(output))
#     # 	json_text = (desc.split("```json"))[1].split("```")[0]
#     # 	json_data = validate_json_text(json_text)
#     # 	print(str(json_data))
#     # 	for items in json_data:
#     # 		item_code = items['item_code']
#     # 		item_name = items['item_name']
#     # 		description = items['description']
#     # 		self.append('items_table', {
#     # 					"item_code" : item_code,
#     # 					"item_name" : item_name,
#     # 					"description" : description
#     # 				})
#     # 		# frappe.db.set_value('Item', item_code, 'description', description)
#         return "Success"
#     except Exception as e:
#         return f"Exception Check Item Description Error: {str(e)}"