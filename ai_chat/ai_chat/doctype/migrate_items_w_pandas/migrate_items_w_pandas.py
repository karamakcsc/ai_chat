import frappe
import pandas as pd
import requests
from frappe.model.document import Document
import os
import time
import frappe
import pandas as pd
# from pandas import to
import requests
import os
import time

class MigrateItemswPandas(Document):

    @frappe.whitelist()
    def translate_text_helper(self, text, source_lang, target_lang):
        df = pd.DataFrame(text)
        dict_text = df.to_dict(orient='records')
        keys = list(dict_text[0].keys())[0]
        url = "https://api.cohere.com/v1/chat"
        headers = {
            "Authorization": "Bearer 9WIy7pDUSFAsLSqrowvxBzIoy9EbLQ45ClLRMjd5",
            "Content-Type": "application/json"
        }
        # # message = f"I will upload an Excel file{text}. I want you to read all the columns inside the Excel file, then translate them from Arabic to English. Then add the new columns translated into English to the Excel file, edit the file itself, and then return it to me."
        message = f"Translate words in list  {dict_text} to En and Ar and in json file with format ```json"+ """{"EN" : en_word , "AR" : ar_word }"""+ " ``` for every dict"
        data = {
                    "model": "command-r-plus",
                    "message": message,
                    "temperature": 0.3,
                    "chat_history": [],
                    "prompt_truncation": "auto",
                    "connectors" : [{"id" : "web-search"}]
                }
        
        # try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        translation_response = response.json()
        output = translation_response["text"]
        json_text = (output.split("```json"))[1].split("```")[0]
        for row in list(json_text):
            row["AR"]

        # print(json_text)
        #     translation = translation_response.get('results', [{}])[0].get('targets', [{}])[0].get('text', '')
        #     return translation
        # except requests.RequestException as e:
        #     frappe.log_error(f"Translation API request failed: {e}", "Translation Error")
        #     return "Translation Error"

    @frappe.whitelist()
    def translate_text(self): 
        # try:
            directory = '/home/erpadmin/frappe-bench/sites/ai.local/'
            public_directory = os.path.join(directory , 'public')
            private_directory = os.path.join(directory , 'private')
            if os.path.exists(public_directory + self.attach_xlsx_file):
                excel_file = public_directory + self.attach_xlsx_file
            elif os.path.exists(private_directory + self.attach_xlsx_file):
                excel_file = private_directory + self.attach_xlsx_file
            else:
                frappe.throw(f"Cannot find the Excel file that was uploaded. Looked in {public_directory} and {private_directory}.")
            df = pd.read_excel(excel_file)
            for col in df.columns:
                if df[col].dtype == object:
                    self.translate_text_helper(df[col], 'ar', 'en')
                    # new_col = f"{col}_en"
                    # df[new_col] = df[col].apply
                    # updated_file_path = excel_file.replace('.xlsx', '_translated.xlsx')
                    # df.to_excel(updated_file_path, index=False)
                    # self.save_translated_file(updated_file_path)
                    # return "Translation and saving process completed."
                # if df[col].dtype == object:  # Check if the column is of string type
                    # new_col = f"{col}_en"
                    # df[new_col] = df[col].apply
            # updated_file_path = excel_file.replace('.xlsx', '_translated.xlsx')
            # df.to_excel(updated_file_path, index=False)
            # self.save_translated_file(updated_file_path)
        #     return "Translation and saving process completed."
        
        # except Exception as e:
        #     frappe.msgprint(f"Error reading Excel file: {e}")
        #     return
        
    # def find_uploaded_file(self, public_directory, private_directory):
    #     public_path = os.path.join(public_directory, self.attach_xlsx_file)
    #     private_path = os.path.join(private_directory, self.attach_xlsx_file)
        
    #     if os.path.exists(public_path):
    #         return public_path
    #     elif os.path.exists(private_path):
    #         return private_path
    #     else:
    #         return None
    @frappe.whitelist()
    def save_translated_file(self, excel_file):
        with open(excel_file, 'rb') as f:
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": os.path.basename(excel_file),
                "is_private": 1,
                "content": f.read(),
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name
            })
            file_doc.save()
            frappe.db.commit()
            frappe.msgprint(f"Translated file uploaded: {file_doc.file_url}")