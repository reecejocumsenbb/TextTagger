import json
import streamlit as st

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

def reset_indices():
    st.session_state.string_i = 0
    st.session_state.key_i = 0

if 'string_i' not in st.session_state:
    reset_indices()

if 'key_i' not in st.session_state:
    reset_indices()

if 'sentences' not in st.session_state:
    st.session_state.sentences = {}

st.title("Sentence Selector")

st.header("Upload File")
file = st.file_uploader("Upload sentences", ".json", on_change=reset_indices)

strings = []

if st.sidebar.button('Download'):
    data_to_save = st.session_state.sentences

    json_string = json.dumps(data_to_save)

    st.sidebar.download_button(label="As .json", data=json_string, file_name='data.json', mime='application/json')

st.sidebar.title('Sentences')
sentences_history = st.sidebar.empty()
sentences_history.text("Nothing here.")
sentences_history.json(st.session_state.sentences)

categories = []



if file is not None:
    file_text = file.read().decode("utf-8")
    data = json.loads(file_text)
    
    string_i = st.session_state.string_i
    key_i = st.session_state.key_i

    if list(data)[key_i] not in st.session_state.sentences:
        st.session_state.sentences[list(data)[key_i]] = []

    strings = data[list(data)[key_i]]

    st.text(f'{string_i} {key_i} {len(strings)}')

    subheader = st.subheader(f'Review sentence #{string_i} for keyword #{key_i}')
    string_to_see = st.empty()
    string_to_see.markdown(f'>{strings[string_i]}')

    col1, col2, col3 = st.columns((1, 1, 10))

    def update_displayed_sentence():
        st.session_state.string_i += 1
        if st.session_state.string_i >= len(strings[string_i]):
            st.session_state.string_i = 0
            st.session_state.key_i += 1
        subheader.subheader(f'Review sentence #{string_i} for keyword #{key_i}')
        string_to_see.markdown(f'>{strings[string_i+1]}')

    if col1.button("Keep"):
        st.session_state.sentences[list(data)[key_i]].append(strings[string_i])
        sentences_history.json(st.session_state.sentences)
        update_displayed_sentence()
    
    if col2.button("Throw"):
        update_displayed_sentence()