import os
import subprocess
import streamlit as st
import spacy
import pandas as pd

def define_matcher(nlp):
    patterns = {
        'adv_adj': [[
            {'POS': 'ADV'},
            {'POS': 'ADJ'},
                ]],
        'noun_verb': [[
            {'POS': 'NOUN'}, 
            {'POS': 'VERB'}
            ]],
        'noun_noun': [[
            {'POS': 'NOUN'},
            {'POS': 'NOUN'}
        ]],
        'adv_verb': [[
            {'POS': 'ADV'},
            {'POS': 'PUNCT', 'OP': '?'},
            {'POS': 'VERB'}
        ]],
        'verb_adp': [[
            {'POS': 'VERB'},
            {'POS': 'ADP'}
        ]],
        'adj_adp': [[
            {'POS': 'ADJ'},
            {'POS': 'ADP'}
        ]],
        'adv': [[
            {'POS': 'ADV'},
        ]]
    }

    matcher = spacy.matcher.Matcher(nlp.vocab, validate=True)
    for key in patterns.keys():
        matcher.add(key, patterns[key])

    return matcher

def define_phrase_matcher(nlp):
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

    patterns = [
            [
                {'POS': {'IN': ['AUX', 'VERB']}, 'OP': '?'},
                {'POS': 'DET', 'OP': '?'},
                {'POS': {'IN': ['NOUN', 'PROPN']}, 'TEXT': {'IN': st.session_state.toi}}
            ],
            [
                {'POS': {'IN': ['AUX', 'VERB']}, 'OP': '?'},
                {'POS': 'ADJ', 'TEXT': {'IN': st.session_state.toi}},
                {'POS': 'ADP', 'OP': '?'}
            ],
            [
                {'POS': {'IN': ['AUX', 'VERB']}, 'OP': '?'},
                {'POS': 'DET', 'OP': '?'},
                {'TEXT': {'IN': st.session_state.toi}, 'POS': 'ADJ'},
                {'POS': 'NOUN'}
            ]
        ]

    phrase_patterns = st.session_state.toi

    #st.text(patterns)

    matcher = spacy.matcher.PhraseMatcher(nlp.vocab, validate=True)
    #matcher.add("patterns", patterns)
    matcher.add("phrase patterns", [nlp.make_doc(phrase) for phrase in phrase_patterns])
    return matcher

def remove_redundant_matches(matches_data):
    for match1 in matches_data.copy():
        match1_start = match1[1]
        match1_end = match1[2]
        for match2 in matches_data.copy():
            match2_start = match2[1]
            match2_end = match2[2]
            if (match1 != match2):
                if (match1_start >= match2_start and match1_end <= match2_end):
                    try:
                        matches_data.remove(match1)
                    except ValueError:
                        pass
                elif (match2_start >= match1_start and match2_end <= match1_end):
                    try:
                        matches_data.remove(match2)
                    except ValueError:
                        pass

def replace_with_alternative(paragraph, start, end, match_type, alternative):
    out = []
    st.text(alternative)
    replacement, structure = alternative
    if match_type == 'adv_adj':
        if structure == 'ADJ':
            out.append(paragraph[:start])
            out.append(replacement)
            out.append(paragraph[end:])
        if structure == 'ADJ NOUN':
            # ? currently assuming that the thing directly after adv_adj is NOUN
            noun = paragraph[end]
            out.append(paragraph[:start])
            out.append(noun.text + ' with')
            out.append(replacement)
            out.append(paragraph[end+1:])
        return out
    if match_type == 'noun_verb':
        out.append(paragraph[:start])
        out.append(replacement)
        out.append(paragraph[end:])
        return out
    if match_type == 'noun_noun':
        out.append(paragraph[:start])
        out.append(replacement)
        out.append(paragraph[end:])
        return out
    if match_type == 'adv_verb':
        out.append(paragraph[:start])
        out.append(replacement)
        out.append(paragraph[end:])
        return out
    if match_type == 'verb_adp':
        out.append(paragraph[:start])
        out.append(replacement)
        out.append(paragraph[end:])
        return out
    if match_type == 'adj_adp':
        out.append(paragraph[:start])
        out.append(replacement)
        out.append(paragraph[end:])
        return out
    if match_type == 'adv':
        out.append(paragraph[:start])
        out.append(replacement)
        out.append(paragraph[end:])
        return out


def chunkify(string: str):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(string)

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

    st.header("DEBUG phrases caught")

    alternatives = {
        'visually impaired': [
            ('blind', 'ADJ'), 
            ('low vision', 'ADJ NOUN')
        ],
        'hearing impaired': [
            ('deaf', 'ADJ'),
            ('hard of hearing', 'ADV ADP NOUN')
        ],
        'brain damage': [
            ('a brain injury', 'DET NOUN NOUN'),
            ('a traumatic brain injury', 'DET ADJ NOUN NOUN')
        ],
        'differently abled': [
            ('disabled', 'VERB')
        ],
        'differently-abled': [
            ('disabled', 'VERB')
        ],
        'blinded by': [
            ('preoccupied with', 'VERB ADP'),
            ('consumed by', 'VERB ADP'),
            ('confused by', 'VERB ADP'),
        ], 
        'blind to': [
            ('ignorant of', 'ADJ ADP'),
            ('ignoring', 'ADJ ADP')
        ],
        'blindly': [
            ('ignorantly', 'ADV'),
            ('naively', 'ADV')
        ]
        }

    matcher = define_phrase_matcher(nlp)

    matches = matcher(doc)
    
    matches_data = []

    for _, start, end in matches:
        string = doc[start:end]
        matches_data.append([str(string), start, end])
           
    remove_redundant_matches(matches_data)

    matches_dataframe = pd.DataFrame(matches_data, columns=['Match', 'Start index', 'End index'])

    st.dataframe(matches_dataframe)

    for match, start, end in matches_data:
        match_tokens = doc[start:end]
        structure_matcher = define_matcher(nlp)
        matches = structure_matcher(doc[start:end])
        for inner_match in matches:
            pattern_name = nlp.vocab.strings[inner_match[0]]
            info_string = f"string '{match}' matched pattern '{pattern_name}'. Alternatives: {', '.join([string[0] for string in alternatives[match]])}.\n\n"

            for i, alternative in enumerate(alternatives[match]):
                info_string += f"for alternative {i}:\n\n {[str(piece) for piece in replace_with_alternative(doc, start, end, pattern_name, alternative)]}\n\n"
            st.info(info_string)
        

def main():
    st.title("spaCy Testing")

    text = st.text_area('Example paragraph')

    chunkify(text)

if __name__ == '__main__':
    main()
