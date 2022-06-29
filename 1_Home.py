import streamlit as st

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.markdown("""
# Home
Welcome to this data collector/tagger! At the moment we have:
* A Quora crawler (Web Quorler - get it?)
* A sentence selection section (Sentence Selector)
* A text tagging section (Text Tagger)
* A testing page for NLP library spaCy (spaCy Test)
""")