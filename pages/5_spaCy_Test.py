from attr import validate
import streamlit as st
import spacy
import pandas as pd

def define_matcher(nlp):
    # region getting toi
    st.session_state.use_default = st.checkbox("Use defaults", value=True)
    file = None
    if not st.session_state.use_default:
        file = st.file_uploader("Upload keywords", ".txt", disabled=st.session_state.use_default)

    if file is not None:
        st.write('file get')

        st.session_state.toi = file.read().split('\n')

    elif st.session_state.use_default:
        file = None
        with open('./scraper/termsofinterest.txt', 'r') as file:
            st.session_state.toi = file.read().split('\n')
    # endregion

    pattern = [{'TEXT': {'IN': st.session_state.toi}}]

    st.text(pattern)

    matcher = spacy.matcher.Matcher(nlp.vocab, validate=True)
    matcher.add("TOI", [pattern])
    return matcher


def chunkify(string: str):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(string)

    st.header("Noun Chunks")

    noun_chunk_data = []

    for chunk in doc.noun_chunks:
        noun_chunk_data.append([chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text])

    noun_chunk_dataframe = pd.DataFrame(noun_chunk_data, columns=['Text', 'Root Text', 'Root Dep', 'Root Head Text'])

    if len(noun_chunk_data) > 0:
        st.dataframe(noun_chunk_dataframe)
    else:
        st.write("No sentence yet")
    
    st.header("Tokens")

    token_data = []

    for token in doc:
        token_data.append([token.text, token.pos_, token.head.text, token.head.pos_,
            str([child for child in token.children])])

    token_dataframe = pd.DataFrame(token_data, columns = ["Text", "Pos", "Head Text", "Head Pos", "Children"])

    if len(token_data) > 0:
        st.dataframe(token_dataframe)
    else:
        st.write("No sentence yet")

    

    st.header("Maybe?")

    matcher = define_matcher(nlp)

    matches = matcher(doc)
    
    matches_data = []

    for _, start, end in matches:
        string = doc[start:end]
        matches_data.append([str(string), start, end])

    matches_dataframe = pd.DataFrame(matches_data, columns=['Match', 'Start index', 'End index'])

    st.dataframe(matches_dataframe)

    


def main():
    st.title("spaCy Testing")

    text = st.text_input('Example sentence')

    chunkify(text)

if __name__ == '__main__':
    main()
