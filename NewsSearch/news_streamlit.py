import streamlit as st
import sys
import pandas as pd
from news_processor import NewsProcessor

keyword_save = ''
headlines = pd.DataFrame()
hf = pd.DataFrame()
news = NewsProcessor()
countries = list(news.COUNTRIES)
countries.sort()
categories = list(news.CATEGORIES)
categories.sort()
st.title('Intelligent News')

# get the keyword to search from the user
keyword = st.sidebar.text_input(label='Enter keyword to search:')
country = st.sidebar.selectbox(label='Country:', options=countries)
category = st.sidebar.selectbox(label='News category:', options=categories)
if keyword and keyword != keyword_save:
    headlines = news.get_top_headlines(keywords=keyword,
                                       country=country,
                                       category=category,
                                       page_size=100)
    if not headlines.empty:
        cols_to_keep = ['title', 'description', 'date', 'url', 'content']
        hf = headlines[cols_to_keep]
    else:
        st.write('No stories found matching those details.')
    keyword_save = keyword

if not hf.empty:
    st.dataframe(hf)
    story = st.selectbox(label='Enter story to inspect:', options=hf['title'].values.tolist())
    stry = hf[hf['title'] == story]
    st.write(stry['content'].values[0])
    st.write(stry['url'].values[0])
