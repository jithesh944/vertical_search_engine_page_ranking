import pandas as pd
import numpy as np
import re
import ast
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import PorterStemmer

import random
from nltk.stem import WordNetLemmatizer


nltk.download('punkt')
nltk.download('wordnet')


def read_csv_files():
    # Dump of the all documents from SEFA page.
    all_publications_csv = pd.read_csv('book_dump.csv',sep=',')
    all_publications_csv = all_publications_csv.set_index('doc_id').drop('Unnamed: 0',axis=1)

    # Dump of books & papers from SEFA page.
    paper_book_csv = pd.read_csv('book_paper_dump.csv',sep=',')
    paper_book_csv = paper_book_csv.set_index('doc_id').drop('Unnamed: 0',axis=1)
    return all_publications_csv,paper_book_csv

def select_required_data(whole_doc,all_publications_csv,paper_book_csv):
    print('select_required_data',whole_doc)
    if whole_doc:

        req_book_df = all_publications_csv
    else:

        req_book_df = paper_book_csv
    return req_book_df


def correcting_req_df(req_book_df_corr):
    req_book_df_corr['keywords'] = (req_book_df_corr['keywords'].map(ast.literal_eval))
    for row in req_book_df_corr.index:
        if (pd.isna(req_book_df_corr['abstract'][row])):
            req_book_df_corr['combine'] =req_book_df_corr['doc_title'] 
        else:
            req_book_df_corr['combine'] = req_book_df_corr['doc_title'] + ' '+req_book_df_corr['abstract']

    req_book_df_corr['combine_len'] = req_book_df_corr['combine'].map(lambda b:len(b))
    return req_book_df_corr

def cleaning_req_df(req_book_df):
    req_book_df['combine']= req_book_df['combine'].map(lambda a:a.lower())
    req_book_df['combine'] =req_book_df['combine'].map(lambda a:re.sub(r'[%s]' % re.escape(string.punctuation), ' ', a))
    stp_words_eng = stopwords.words('English')
    document_test_list = list()
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()

    for doc in req_book_df['combine']:
        # Remove the doubled space
        document_test = re.sub(r'\s{2,}', ' ', doc)
        
        tokens = nltk.word_tokenize(document_test)
        next_text = list()
        for word in tokens:
            if (word.lower() not in stp_words_eng) and (word != "’") :
                next_text.append(lemmatizer.lemmatize(word))
                
        document_test_list.append(next_text)
    req_book_df['combine'] = document_test_list
    return req_book_df

def find_unique_words(req_book_df):
    req_book_df['unique_words'] = [list(set(doc)) for doc in req_book_df['combine']]
    unique_words_list= [ word for words_list in req_book_df['unique_words']  for word in words_list]
    unique_words_list =(set(unique_words_list))
    return req_book_df,unique_words_list

def initiate_data_process(whole_doc):
    all_publications_csv,paper_book_csv = read_csv_files()
    req_book_df = select_required_data(whole_doc,all_publications_csv,paper_book_csv)
    req_book_df_corr = correcting_req_df(req_book_df)
    req_book_df_clean= cleaning_req_df(req_book_df_corr)
    req_book_df_clean_updt,unique_words_list=find_unique_words(req_book_df_clean)
    return req_book_df_clean_updt,unique_words_list