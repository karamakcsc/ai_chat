# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

# import frappe
# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

from ai_chat.ai_chat.doctype import chat
import frappe
import cohere
import uuid
import json
from frappe.model.document import Document

class ItemCommonlyKnown(Document):
    pass

cohere_api_key = "cFfUviEu0HQlImtOlBAxdQ5TRpAVP9cLGZieXaBd"
co = cohere.Client(cohere_api_key, client_name="frappe-dev")

history = []

@frappe.whitelist()
def generate_response(cid, token, dynamic_doc):
    try:

        if not token:
            raise frappe.msgprint({
                "title": "Alert",
                "message": "Error loading. not authorized, make sure to have valid API token",
                "indicator": "red"})
        if cid == "" or cid is None:    
            cid = str(uuid.uuid4())
        user_message = f'''Give me synonyms with the same meaning {dynamic_doc} in Arabic and English as json format:
                arabic and english tags'''
        history.append(user_message)
        stream = co.chat_stream(message=user_message, conversation_id=cid, model='command-r-plus', connectors=[], temperature=0.3)
        output = ""
        for idx, response in enumerate(stream):
            if response.event_type == "text-generation":
                output += response.text
        print(output)
        json_data = (output.split("```json"))[1].split("```")[0]
        json_text = json.loads(json_data)
        arabic_words = json_text["arabic"]
        english_words = json_text["english"]
        if arabic_words:
            cleaned_arabic_words = [word for word in arabic_words]
        if english_words:    
            cleaned_english_words = [word for word in english_words]
        arabic_words_list = []
        english_words_list = []
        for words in cleaned_arabic_words:
            arabic_words_list.append(words + '\n')
        for words in cleaned_english_words:
            english_words_list.append(words + '\n')
        return arabic_words_list, english_words_list

    except Exception as e:
         return f" Exception Generate Response Error: {str(e)} "

#####################################################

#zaid code:

# @frappe.whitelist()
# def base_request_data():
#     base_url =  'http://147.182.251.32:8000/api/resource'
#     headers = {
#         "Authorization": "Basic NDNlNjY0ZTk4MjJmZDFjOjBlN2FiOTljNzBhNmE1OQ==",
#         "Content-Type": "application/json"
#     }
#     return base_url , headers

# @frappe.whitelist()
# def get_supplier(supplier_json = None):
#     base_url, headers = base_request_data()
#     supplier_list = []

#     try:    
#         if supplier_json in [None , "" , " "]:
#             return False
#         response = requests.get(base_url + '/Supplier', headers=headers)
#         response_json =  response.json()
#         data_json = response_json["data"]

#         for supplier in data_json:
#             supplier_list.append(supplier['name'])
    
#         for supplier in supplier_list:
#             if supplier == supplier_json or supplier in supplier_json:
#                 return supplier 
#         return False
        
#     except Exception as e:
#         return f" Exception Validate Item Description Error: {str(e)} "


################## MK Code ##########

# @frappe.whitelist()
# def search_in_uom(basic_measurement_unit):
#     basic_measurement_unit_lower = basic_measurement_unit.lower()
#     try:
#         uom_data = frappe.db.sql("""
#                                 SELECT name
#                                 FROM `tabUOM`
#                                 """, as_dict = True)
        
#         if uom_data and uom_data[0]:
#             for uoms in uom_data:
#                 uom_names = uoms.name
#             if uom_names:
#                 if basic_measurement_unit_lower in uom_names:
#                     return basic_measurement_unit
#                 if basic_measurement_unit_lower not in uom_names:
#                     all_commonly_known_sql = frappe.db.sql("""
#                                                             SELECT  commonly_known
#                                                             FROM `tabItem Commonly Known`
#                                                         """ , as_dict = True)
                    
#                     if all_commonly_known_sql and all_commonly_known_sql[0]:
#                         for all_commonly_known in all_commonly_known_sql:
#                             commonly_known_name = all_commonly_known.commonly_known
#                         if commonly_known_name:
#                             if basic_measurement_unit in commonly_known_name:
#                                 return basic_measurement_unit
#                             if basic_measurement_unit not in commonly_known_name:
#                                 return False
#     except Exception as e:
#         return f" Exception Search In Uom Error: {str(e)} "
    
########## MK Code ##################    