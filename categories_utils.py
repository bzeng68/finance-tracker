import streamlit as st
import json
import os

class CategoriesUtils:
    def __init__(self):
        if "categories" not in st.session_state:
            st.session_state.categories = {
                "Uncategorized": []
            }
            
        if os.path.exists("categories.json"):
            with open("categories.json", "r") as f:
                st.session_state.categories = json.load(f)
                
    @staticmethod
    def add_category(category_name):
        if category_name not in st.session_state.categories.keys():
            st.session_state.categories[category_name] = []
              
    @staticmethod
    def save_categories():
        with open("categories.json", "w") as f:
            json.dump(st.session_state.categories, f)
         
    @staticmethod
    def add_keyword_to_category(category, keyword):
        keyword = keyword.strip()
        if keyword and keyword not in st.session_state.categories[category]:
            st.session_state.categories[category].append(keyword)
    
    @staticmethod
    def get_categories():
        return st.session_state.categories