import frappe
import requests
import json
from datetime import date

################################################################################ From Mahmoud 
# import mysql.connector

# class MySQLConnector:
#     def __init__(self, host, username, password, database):
#         self.host = host
#         self.username = username
#         self.password = password
#         self.database = database

#     def search(self, query):
#         cnx = mysql.connector.connect(
#             user=self.username,
#             password=self.password,
#             host=self.host,
#             database=self.database
#         )
#         cursor = cnx.cursor()
#         cursor.execute("SELECT * FROM expenses WHERE description LIKE %s", (f"%{query}%",))
#         results = cursor.fetchall()
#         return [{"id": row[0], "date": row[1], "amount": row[2], "description": row[3]} for row in results]
####################################################################################



def base_request_data():
    base_url =  'http://147.182.251.32:8000/api/resource'
    headers = {
        "Authorization": "Basic NDNlNjY0ZTk4MjJmZDFjOjBlN2FiOTljNzBhNmE1OQ==",
        "Content-Type": "application/json"
    }
    return base_url , headers

def base_request_cohere_data():
    url = 'https://api.cohere.ai/v1/chat'
    headers = {
        "Authorization": "Bearer lc9DVbwzyvxgzwbWXZgcmtVxaJk7IyrmMTX2RV5P",
        "Content-Type": "application/json"
    }
    return url, headers

@frappe.whitelist()
def create_purchase_order(ai_json, supplier, company):
    base_url , headers = base_request_data()
    try:
        json_text = ai_json
        data_ai = validate_json_text(json_text)
        # frappe.throw(str(data_ai))
        order = data_ai['order']['items']
        supplier_json = data_ai['supplier']
        supplier_ = get_supplier(supplier_json)
        if not supplier_:
            supplier_ = supplier
        po_items = []
        if order:
            for item in order:
                item_code_po = ''
                item_code = item['item']
                uom = None
                rate = None
                qty = None
                warehouse = 'Stores - KCSCD'
                json_qty = item['qty']
                commonly_known_as = item['commonly_known_as']
                basic_measuring_unit = item['basic_measuring_unit']
                item_code_psi= process_search_items(item_code)
                if item_code_psi:
                    item_code_po = item_code_psi
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
                            else:
                                item_code_item_alterantive = item_alternative(item_code)
                                if item_code_item_alterantive:
                                    item_code_po = item_code_item_alterantive
                if not item_code_po:
                    frappe.throw(f'Item {item_code} Does Not Exist.')
                uom = search_in_uom(basic_measuring_unit)
                rate = get_item_rate(item_code_po, uom)
                qty =  qty_check(json_qty, item_code_po, warehouse)  
                if not qty :
                    frappe.throw(f'Create Purchase Order Error in {item_code_po}.')
                dict_po = {
                    'item_code' : item_code_po,
                    'item_name' : item_code_po,
                    'uom' : uom,
                    'rate' : rate,
                    'warehouse' : warehouse,
                    'qty' : qty,
                    'company' : company,
                    'supplier' : supplier_,
                    "schedule_date": str(date.today())
                }
                po_items.append(dict_po)
        # print(po_items)
        # frappe.throw(str(po_items))
        url = base_url + f'/Purchase Order'
        data = {
            "doctype": "Purchase Order ",
            "naming_series": "PUR-ORD-.YYYY.-",
            "title": supplier_,
            "supplier": supplier_,
            "transaction_date": str(date.today()),
            "currency": "JOD",
            "company": company,
            "docstatus": 0,
            "items": po_items
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 201, 202]:
        # frappe.throw(str(po_items))
            return po_items
        else:
            return f"There is an error in the status code with error: {response.text}"
    except Exception as e:
        # frappe.msgprint(f"Error occurred at line {e.__traceback__.tb_lineno}")
        # frappe.msgprint("Exception Create Purchase Order Error.")
        return f"Exception Create Purchase Order Error: {str(e)}"

def process_search_items(json_item_code):
    try:
            data_items = frappe.db.sql(""" SELECT item_code, item_name FROM `tabItem` WHERE has_variants = 0""", as_dict = True)
            if data_items and data_items[0]:
                for item_dict in data_items:
                    if json_item_code == item_dict["item_code"]:
                        return item_dict["item_code"]
                    if json_item_code == item_dict["item_name"] or json_item_code in item_dict["item_name"]:
                        return item_dict["item_code"]
                else:
                    return False  
    except Exception as e:
        return f"Exception Proccess Search Items Error:  {str(e)}"

def search_in_commonly_known_names(item_name, commonly_known_as):
    base_url , headers = base_request_data()
    try:
        doc_name = 'Commonly Known'
        item_name_without_spaces = item_name.replace(' ', '')
        all_commonly_knwon_sql = frappe.db.sql(f"""SELECT  name , document , commonly_known FROM `tab{doc_name}` """ , as_dict = True)
        if all_commonly_knwon_sql and all_commonly_knwon_sql[0]:
            #### check commonly known as
            for all_commonly_knwon in all_commonly_knwon_sql:
                #### Read data for item
                commonly_known_name = all_commonly_knwon.name
                commonly_known_item = all_commonly_knwon.document
                commonly_known_data = all_commonly_knwon.commonly_known
                commonly_known_data_without_spaces = commonly_known_data.replace(' ' ,'')
                if commonly_known_item and commonly_known_data:
                    if item_name_without_spaces in commonly_known_data_without_spaces:
                        ## the item is exist but in other name
                        try:
                            if commonly_known_as not in commonly_known_data_without_spaces:
                                new_commonly_known_data = commonly_known_data + '\n' + commonly_known_as
                                try:
                                    frappe.db.set_value(f'{doc_name}', f'{commonly_known_name}', 'commonly_known', new_commonly_known_data)
                                except Exception as e:
                                    return f'Exception: There are Error in Request :{e}'
                            else:
                                pass
                        except Exception as e:
                            return f'Exception: There are Error in Commonly Known: {e}'
                        return commonly_known_item
        return False
    except Exception as e :
        return f'Exception Search In Commonly Known Names: Error: {e}'

def validate_item_description(item_code):
    try:
        all_items_in_sql = frappe.db.sql(f"""SELECT name, description FROM `tabItem` WHERE has_variants = 0""", as_dict=True)
        if all_items_in_sql and all_items_in_sql[0]:
            for item_info in all_items_in_sql:
                data_item_code = item_info.name
                description = item_info.description
                if item_code in description:
                    return data_item_code
            else:
                return False
        else:
            return False
    except Exception as e:
        return f"Exception Validate Item Description Error: {str(e)}"

def qty_check(json_qty, item_code, warehouse):
    float_json_qty = float(json_qty)
    try:
        bin_query = frappe.db.sql(f""" 
                                  SELECT actual_qty
                                  FROM `tabBin`
                                  WHERE item_code = '{item_code}' AND warehouse = '{warehouse}'
                                  """, as_dict=True)
        if bin_query and bin_query[0]:
            for qty in bin_query:
                data_actual_qty = qty.actual_qty
                if data_actual_qty >= float_json_qty:
                    return float_json_qty
                else:
                    return False
        else:
            return False
    except Exception as e:
        return f"Exception qty_check in Bin Proccess Error: {str(e)}"

def get_supplier(supplier_json = None):
    base_url, headers = base_request_data()
    supplier_list = []

    try:  

        if supplier_json in [None , "" , " "]:
            return False
        response = requests.get(base_url + '/Supplier', headers=headers)
        response_json =  response.json()
        data_json = response_json["data"]

        for supplier in data_json:
            supplier_list.append(supplier['name'])
    
        for supplier in supplier_list:
            if supplier == supplier_json or supplier in supplier_json:
                return supplier 
        return False
        
    except Exception as e:
        return f" Exception Get Supplier Error: {str(e)} "

def get_item_rate(item_code, uom):

    try:

        item_rate = frappe.db.sql(f""" 
                                  SELECT price_list_rate FROM `tabItem Price`
                                   WHERE item_code = '{item_code}' AND uom = '{uom}' """,as_dict=True)
        
        if item_rate and item_rate[0] and item_rate[0]['price_list_rate']:
            return float(item_rate[0]['price_list_rate'])
        else:
            return False
    
    except Exception as e:
        return f" Exception Get Item Rate Error: {str(e)} "
    
def search_in_uom(basic_measurement_unit):
    basic_measurement_unit_lower = basic_measurement_unit.lower()
    try:

        uom_data = frappe.db.sql("""
                                SELECT name
                                FROM `tabUOM`
                                """, as_dict = True) 
        if uom_data and uom_data[0]:
            for uoms in uom_data:
                if basic_measurement_unit_lower == uoms.name.lower() :
                    return uoms.name
        all_commonly_known_sql = frappe.db.sql("""
                                                    SELECT document ,  commonly_known
                                                    FROM `tabCommonly Known` WHERE doc_type = 'UOM'
                                                """ , as_dict = True)
        if all_commonly_known_sql and all_commonly_known_sql[0]:
            for all_commonly_known in all_commonly_known_sql:
                    all_commonly_known_without_spaces = all_commonly_known.commonly_known.replace(" " , "")
                    if (all_commonly_known_without_spaces == basic_measurement_unit ) or (basic_measurement_unit in  all_commonly_known_without_spaces):
                        return str(all_commonly_known.document)
        return False
    
    except Exception as e:
        return f" Exception Search In Uom Error: {str(e)} "

@frappe.whitelist()
def item_alternative(item_code):
    try:

        alternative=frappe.db.sql(f""" 
                                  SELECT alternative_item_code FROM `tabItem Alternative`
                                   WHERE item_code = '{item_code}' """,as_dict=True)
        alternative_lst = list()
        if alternative and alternative[0] and alternative[0]['alternative_item_code']:
            for alt in alternative:
                alternative_lst.append(alt['alternative_item_code'])

        original=frappe.db.sql(f"""
                                  SELECT item_code FROM `tabItem Alternative`
                                   WHERE alternative_item_code = '{item_code}' AND two_way = 1 """,as_dict=True)
        original_lst = list()
        if original and original[0] and original[0]['item_code']:
            for ori in original:
                original_lst.append(ori['item_code'])

        main_lst = original_lst + alternative_lst
        if len(main_lst) != 0:
            return main_lst
        return False
    
    except Exception as e:
        return f" Exception Item Alternative Error: {str(e)} " 

# @frappe.whitelist()
# def validate_json_text(json_text):
#     try: 
        
#         _json = json.loads(json_text)
#         return _json
#     except Exception as e : 
#         message = f'The json file has Error. edit it to be in correct json format: {json_text}'
#         url , headers  = base_request_cohere_data()
#         data = {
#                     "model": "command-r-plus",
#                     "message": message,
#                     "temperature": 0.3,
#                     "chat_history": [],
#                     "prompt_truncation": "auto",
#                 }
#         response = requests.post(url, headers=headers, json=data)
#         response_json = response.json()
#         response_text = response_json["text"]
#         json_response = response_text.split("json\n")[1].split("\n\n")[0]
#         return json_response
    # except json.JSONDecodeError:
    #     frappe.throw("Invalid JSON Data")
    #     return {"error": "Invalid JSON data"}
    # except requests.RequestException as e:
    #     frappe.throw(f"API Request Failed: {str(e)}")
    #     return {"error": f"API request failed: {str(e)}"}
    # except Exception as e:
    #     frappe.throw(f"Error {str(e)}")
    #     return {"error": f"Exception Create Purchase Order: {str(e)}"}

@frappe.whitelist()
def validate_json_text(json_text):
    try:
        _json = json.loads(json_text)
        return _json
    except Exception as e:
        message = f'The json file has Error. edit it to be in correct json format: {json_text}'
        url, headers = base_request_cohere_data()
        data = {
            "model": "command-r-plus",
            "message": message,
            "temperature": 0.3,
            "chat_history": [],
            "prompt_truncation": "auto",
        }
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        response_text = response_json.get("text", "")
        start_index = response_text.find('{')
        end_index = response_text.rfind('}')
        
        if start_index != -1 and end_index != -1:
            json_response = response_text[start_index:end_index+1]
            try:
                return json.loads(json_response)
            except json.JSONDecodeError:
                return f"Failed to parse JSON: {json_response}"
        else:
            return f"No valid JSON found in the response: {response_text}"
  
# @frappe.whitelist()
# def create_uom(ai_json):
#     base_url , headers = base_request_data()
#     data_ai = json.loads(ai_json)
#     items = data_ai['order']
#     json_uom = []
#     uom_check = []

#     for item in items:
#         uom = item["basic_measuring_unit"]
#         uom_upper = uom.upper()
#         uom_lower = uom.lower()
#         dict_uom = {
#             "uom": uom
#         }
#         json_uom.append(dict_uom)
#         uom_check.extend([uom, uom_upper, uom_lower])

#     placeholders = ','.join(['%s' for _ in uom_check])
#     query = frappe.db.sql(f"""
#                   SELECT uom_name, enabled
#                   FROM `tabUOM`
#                   WHERE name IN ({placeholders})
#                   """, tuple(uom_check), as_dict=True)

#     existing_uoms = {uom['uom_name']: uom for uom in query}

#     new_uoms = []
#     for uom_dict in json_uom:
#         uom = uom_dict['uom']
#         if uom not in existing_uoms:
#             new_uoms.append({
#                 "name": uom,
#                 "enabled": 1,
#                 "uom_name": uom,
#                 "must_be_whole_number": 0,
#                 "doctype": "UOM"
#             })
#         if existing_uoms[uom]['enabled'] == 0:
#             frappe.db.set_value('UOM', uom, 'enabled', 1)
#             # payload = json.dumps({
#             #     "enabled": 1
#             # })
#             # response = requests.put(base_url + '/UOM' + f'/{uom}' , headers=headers, data=payload)  

#     if new_uoms:
#         url = base_url + '/UOM'

#         responses = []
#         for uom_data in new_uoms:
#             response = requests.post(url, headers=headers, json=uom_data)
#             responses.append(response.json())

#         return responses
                
#     return {"message": "No new UOMs to create"}

######################################################################################

# @frappe.whitelist()
# def uom_search_process(item_code, basic_measurement_unit, rate):
#     url , headers = base_request_cohere_data()
#     try:
#         uom_query = frappe.db.sql(f""" SELECT stock_uom FROM `tabItem` WHERE item_code = '{item_code}' """)
#         uom_query_lower = uom_query[0][0]

#         uoms_data = frappe.db.sql(f""" SELECT  tucd.uom 
#                                       FROM  `tabUOM Conversion Detail` tucd 
#                                       WHERE parent = '{item_code}'
#                                       GROUP BY tucd.uom
#                                   """)
#         # return uoms_data
#         if uom_query and uom_query[0]:
#             if uom_query_lower.lower() == basic_measurement_unit.lower():
#                 return uom_query
#             if uom_query != basic_measurement_unit:
#                 message = f'''I have an item with this unit of measure {basic_measurement_unit}  and the rate of {rate} and 
#                 i have this list of units of measure in the system {uoms_data} what alternative unit of measure can i use 
#                 based on the uoms that i have in the system, if there is more than 1 uom choose the most appropriate uom,
#                 use the correct conversion rate for the units of measure,
#                 and only return from the list in the system, 
#                 give me as json format: UOM and Rate tags '''
                
#                 data = {
#                     "model": "command-r-plus",
#                     "message": message,
#                     "temperature": 0.3,
#                     "chat_history": [],
#                     "prompt_truncation": "auto",
#                     "connectors" : [{"id" : "web-search"}]
#                 }
#                 response = requests.post(url, headers=headers, json=data)
#                 if response.status_code in [200, 201, 202]:
#                     response_json = response.json()
#                     output = response_json["text"]
#                     # return output
#                     json_text = (output.split("```json"))[1].split("```")[0]
#                     json_data = validate_json_text(json_text)
#                     return json_data
#                 else:
#                     return f"There is an error in the status code with error: {response.text}"
#     except Exception as e:
#         return f"Exception UOM Serach Proccess Error: {str(e)}"