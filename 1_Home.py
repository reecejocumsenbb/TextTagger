import streamlit as st

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.markdown("""
# Home
Welcome to the Inclusive Language API data website thingy! At the moment we have:
* A text tagging section (Text Tagger)
* A Quora crawler (Web Quorler - get it?)

More things should appear as we go, but I can't make any promises!
""")