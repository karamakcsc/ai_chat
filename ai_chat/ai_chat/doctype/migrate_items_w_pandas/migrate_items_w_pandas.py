# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
import requests
from frappe.model.document import Document
from frappe.utils.file_manager import get_file

class MigrateItemswPandas(Document):

    def translate_text_helper(self, text, source_lang, target_lang):
        url = "https://api.cohere.com/predict"
        headers = {
            "Authorization": "lc9DVbwzyvxgzwbWXZgcmtVxaJk7IyrmMTX2RV5P",  # Replace with your API key
            "Content-Type": "application/json"
        }
        data = {
            "inputs": [
                {
                    "source": text,
                    "language": source_lang,
                    "type": "text/plain"
                }
            ],
            "settings": {
                "targetLanguages": [target_lang]
            }
        }
        response = requests.post(url, headers=headers, json=data)
        translation = response.json()['results'][0]['targets'][0]['text']
        return translation

    def translate_text(self):
        # Load the attached Excel file
        file_data = frappe.get_doc("File", self.attach_xlsx_file)
        file_path = frappe.get_site_path("private", "files", file_data.file_name)
        
        df = pd.read_excel(file_path)

        # Translate Arabic text to English and add new columns
        for col in df.columns:
            if df[col].dtype == object:  # Check if the column is of string type
                new_col = f"{col}_en"
                df[new_col] = df[col].apply(lambda x: self.translate_text_helper(x, 'ar', 'en') if pd.notnull(x) else None)

        # Save the DataFrame back to Excel file
        updated_file_path = file_path.replace('.xlsx', '_translated.xlsx')
        df.to_excel(updated_file_path, index=False)

        # Attach the updated file to the document
        self.save_translated_file(updated_file_path)
        frappe.msgprint("Translation and saving process completed.")

    def save_translated_file(self, file_path):
        with open(file_path, 'rb') as f:
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": file_path.split('/')[-1],
                "is_private": 1,
                "content": f.read(),
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name
            })
            file_doc.save()
            frappe.db.commit()
            frappe.msgprint(f"Translated file uploaded: {file_doc.file_url}")
