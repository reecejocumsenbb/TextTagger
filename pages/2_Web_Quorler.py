import streamlit as st
import scraper.quorascraper as qs
import chime

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

chime.theme('material')

st.title("Web Quorler")
st.header("Parameters")

if 'toi' not in st.session_state:
    st.session_state.toi = []

if 'use_default' not in st.session_state:
    st.session_state.use_default = True

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

col1, col2 = st.columns((6, 10))

posts_per_keyword = col1.number_input("Number of sentences scraped per keyword", min_value = 0, max_value = 1000, value=20)

if st.button("Start scraping"):
    st.header("Scraping")
    quorler_ouput = st.container()

    scraper = qs.QuoraScraper(prefix='https://www.quora.com/search?q="',
            keywords=st.session_state.toi, suffix='"&type=answer', posts_per_keyword=posts_per_keyword, is_streamlit=True, output_container=quorler_ouput)
    scraper.scrape()
    chime.success()