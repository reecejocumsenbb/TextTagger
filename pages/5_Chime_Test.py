import streamlit as st
import chime

st.title("Chime Test")

chime.theme('material')
col1, col2, col3, col4 = st.columns((1, 1, 1, 1))
if col1.button('success'):
    chime.success()
    
if col2.button('info'):
    chime.info()

if col3.button('warning'):
    chime.warning()

if col4.button('error'):
    chime.error()