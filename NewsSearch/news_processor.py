from newsapi import NewsApiClient
from newsapi import const
from pandas.tseries.offsets import BDay
import pandas as pd
import numpy as np
import datetime
import sys
import traceback
import warnings
import spacy
from textblob import TextBlob
from yake import KeywordExtractor


class NewsProcessor(object):
    """ NewsProcessor class:

        This class connects to the News API (https://newsapi.org/) and is able to extract the following:
        (1) top headlines
        (2) every story - historic search
        (3) news sources

        Author: Tegan Asprey
        Created: 10 Jan 2022
        Last Modified: 10 Jan 2022
    """

    API_KEY = '*******'
    COUNTRIES = const.countries
    CATEGORIES = const.categories
    LANGUAGES = const.languages
    SORT_METHODS = const.sort_method

    def __init__(self):
        """ Constructor
        :return: (NewsProcessor) - an instance of NewsProcessor
        """
        try:
            self.news_api = NewsApiClient(api_key=self.API_KEY)
            self.nlp = spacy.load("en_core_web_md")
            self.keyword_extractor = KeywordExtractor()
        except Exception as e:
            print(e)

    def get_top_headlines(self, keywords=None, sources=None, language='en',
                          country=None, category=None, page_size=None, page=None):
        """ Method to fetch the top headlines from the News API
        :param keywords: (str) - the keywords to search
        :param sources: (str) - the sources to use in the search
        :param language: (str) - the 2-letter language code
        :param country: (str) - the 2-letter ISO country code
        :param category: (str) - the news category to use
        :param page_size: (int) - the number of rows to return (max 100)
        :param page: (int) - used to page through the results if there are more than page_size results
        :return: (DataFrame) - the new search results
        """
        data = None
        try:
            results = self.news_api.get_top_headlines(q=keywords, sources=sources,
                                                      language=language, country=country, category=category,
                                                      page_size=page_size, page=page)
            d = pd.json_normalize(results)
            if not d.empty:
                if 'articles' in d.columns:
                    data = pd.json_normalize(d['articles'][0])
                    data['date'] = pd.to_datetime(data['publishedAt'])
        except Exception as e:
            print(e)
        finally:
            return data

    def get_everything(self, keywords=None, keywords_title=None, sources=None, domains=None, exclude_domains=None,
                       from_date=None, to_date=None, language='en', sort_by=None, page_size=None, page=None):
        """ Method to fetch news historic news data from the News API
        :param keywords: (str) - the keywords to search
        :param keywords_title: (str) - the keywords to search in the title field only
        :param sources: (str) - the sources to use in the search
        :param domains: (str) - the domains to use in the search
        :param exclude_domains: (str) - the domains to exclude for the search
        :param from_date: (str) - the string representation of the start date for the search
        :param to_date: (str) - the string representation of the end date for the search
        :param language: (str) - the 2-letter language code
        :param sort_by: (str) - the field by which to sort the results set
        :param page_size: (int) - the number of rows to return (max 100)
        :param page: (int) - used to page through the results if there are more than page_size results
        :return: (DataFrame) - the new search results
        """
        data = None
        try:
            results = self.news_api.get_everything(q=keywords, qintitle=keywords_title, sources=sources,
                                                   domains=domains, exclude_domains=exclude_domains,
                                                   from_param=from_date, to=to_date, language=language,
                                                   sort_by=sort_by, page=page, page_size=page_size)
            d = pd.json_normalize(results)
            if not d.empty:
                if 'articles' in d.columns:
                    data = pd.json_normalize(d['articles'][0])
                    data['date'] = pd.to_datetime(data['publishedAt'])
        except Exception as e:
            print(e)
        finally:
            return data

    def get_sources(self, category=None, language=None, country=None):
        """ Method to fetch the sources available from the News API
        :param category: (str) - the news category
        :param language: (str) - the 2-letter language code
        :param country: (str) - the 2-letter ISO country code
        :return: (DataFrame) - the available sources
        """
        data = None
        try:
            results = self.news_api.get_sources(category=category, language=language, country=country)
            d = pd.json_normalize(results)
            if not d.empty:
                if 'sources' in d.columns:
                    data = pd.json_normalize(d['sources'][0])
        except Exception as e:
            print(e)
        finally:
            return data

    def featurize_results(self, df):
        """ Method to process all titles, descriptions and contents and featurize into a new results DataFrame
        :param df: (DataFrame) - the results from calling either headlines or everything
        :return: (DataFrame) - featurized data set
        """
        data = None
        try:
            pass
        except Exception as e:
            print(e)
        finally:
            return data

    def process_text(self, text):
        """ Method to process the text provided using TextBlob and spacy
        :return: named_entities (dict) - the named entities recognized
        :return: nouns (dict) - the nouns of the text and their pos tags
        :return: verbs (dict) - the verbs of the text and their pos tags
        :return: sentiment_polarity (float) - the polarity of the sentiment score (-1 = negative; 1 = positive)
        :return: subjectivity (float) - the subjectivity of the sentiment score (1 = personal opinion)
        :return: noun_phrases (WordList) - the set of noun phrases  by TextBlob
        :return: keywords (list of tuples) - the keyword phrases extracted by yake
        """
        try:
            # use TextBlob to parse and process the text
            blob = TextBlob(text)
            sentiment_polarity = blob.polarity
            subjectivity = blob.subjectivity
            noun_phrases = blob.noun_phrases

            # use yake to extract keyword phrases
            keywords = self.keyword_extractor.extract_keywords(text)

            # use spacy to parse the text
            doc = self.nlp(text)

            # extract NERs
            named_entities = {}
            for ent in doc.ents:
                named_entities[ent.text] = ent.label_

            # extract nouns and verbs
            nouns = {}
            verbs = {}
            for tok in doc:
                if tok.tag_[:2] == 'NN':
                    nouns[tok.text] = tok.tag_
                if tok.tag_[:2] == 'VB':
                    verbs[tok.text] = tok.tag_
            return named_entities, nouns, verbs, sentiment_polarity, subjectivity, noun_phrases, keywords
        except Exception as e:
            print(e)


if __name__ == '__main__':
    news = NewsProcessor()
    # fetch the latest headlines
    headlines = news.get_top_headlines(keywords='Coronavirus',
                                       country='ca',
                                       category='business',
                                       page_size=100)

    # featurize all stories
    features = news.featurize_results(headlines)

    # store in database

    print('Finished NewsProcessor unit test.')