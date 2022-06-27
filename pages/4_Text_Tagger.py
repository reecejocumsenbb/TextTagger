import io
import json
import streamlit as st
import re
import time

def reset_indices():
    st.session_state.string_i = 0
    st.session_state.key_i = 0

def string_rep_of_tags(container):
    if len(list(st.session_state.string_labels)) != 0:
        inner_container = container.container()
        all_tags = st.session_state.string_labels
        string = ""
        if len(all_tags) == 0:
            string = "Nothing yet."
        else:
            for num, x in enumerate(all_tags):
                string += f'{num}: {", ".join(x) if not len(x) == 0 else "Nothing"}\n'
        inner_container.text(string)

def string_rep_of_seq(container):
    if len(list(st.session_state.string_seq_to_seq)) != 0:
        inner_container = container.container()
        all_text = st.session_state.string_seq_to_seq
        string = ""
        if len(all_text) == 0:
            string = "Nothing yet."
        else:
            for num, x in enumerate(all_text):
                string += f'{num}: {x}\n'
        inner_container.text(string)

if 'string_i' not in st.session_state:
    reset_indices()

if 'string_labels' not in st.session_state:
    st.session_state.string_labels = []

if 'string_seq_to_seq' not in st.session_state:
    st.session_state.string_seq_to_seq = []

st.title("Text Tagger")

st.header("Upload File")
file = st.file_uploader("Upload data to be classified", ".json", on_change=reset_indices)

strings = []

if st.sidebar.button('Download'):
    data_to_save = {'categorized': st.session_state.string_labels, 'seq_to_seq': st.session_state.string_seq_to_seq}
    
    #st.sidebar.json(data_to_save)

    json_string = json.dumps(data_to_save)

    st.sidebar.download_button(label="As .json", data=json_string, file_name='data.json', mime='application/json')

st.sidebar.title('Tagging History')
tags_history = st.sidebar.empty()
tags_history.text("Nothing here.")
string_rep_of_tags(tags_history)

st.sidebar.title('Seq-to-seq History')
seq_to_seq_history = st.sidebar.empty()
seq_to_seq_history.text("Nothing here.")
string_rep_of_seq(seq_to_seq_history)


categories = []

with open('categories.txt', 'r') as category_file:
    categories = category_file.read().split('\n')

if file is not None:
    file_text = file.read().decode("utf-8")
    data = json.loads(file_text)
    
    string_i = st.session_state.string_i
    key_i = st.session_state.key_i

    strings = data[list(data)[key_i]]

    subheader = st.subheader(f'Review sentence #{string_i}')
    string_to_see = st.empty()
    string_to_see.markdown(f'>{strings[string_i]}')

    category_boxes = []

    st.markdown("#### Categorical")    
    for category in categories:
        category_boxes.append(st.checkbox(category, value=False))

    st.markdown("#### Sequence-to-sequence")
    text_to_change = st.empty()
    text = text_to_change.text_area(label="Change the phrasing of this text to something more inclusive.", value=strings[string_i])


    if st.button("Next", disabled=(string_i + 1 >= (len(strings)-1))):
        st.session_state.string_i += 1
        applied_categories = [categories[i] for i, x in enumerate(category_boxes) if x]
        st.session_state.string_labels.append(applied_categories)
        st.session_state.string_seq_to_seq.append(text)
        string_rep_of_tags(tags_history)
        string_rep_of_seq(seq_to_seq_history)
        subheader.subheader(f'Review sentence #{string_i+1}')
        string_to_see.markdown(f'>{strings[string_i+1]}')
        text_to_change.text_area(label="Change the phrasing of this text to something more inclusive.", value=strings[string_i+1])