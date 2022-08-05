import pandas as pd
import numpy as np
from collections import OrderedDict

def get_single_term_freq(unique_words_list,req_book_df):
    term_freq_dict = {}
    for doc_id in req_book_df.index.values:
        term_freq_dict[doc_id] = dict()
    for single_word in unique_words_list:
        for doc_id,doc in zip(list(req_book_df.index.values),req_book_df['combine']):
            term_freq_dict[doc_id][single_word] = doc.count(single_word)

    return term_freq_dict


def get_word_to_doc_freq(unique_words_list,req_book_df):
    
    word_freq_dict = {}
    for word in unique_words_list:
        frq = 0
        for doc in req_book_df['combine']:
            if word in doc:
                frq = frq + 1
        word_freq_dict[word] = frq
    return word_freq_dict
    

def get_idf(unique_words_list,word_freq_dict,req_book_df):
    idf_dict= {} 
    for word in unique_words_list:     
        idf_dict[word] = np.log10((len(req_book_df)+1) / word_freq_dict[word])
    return idf_dict

def calc_tfidf(unique_words_list,term_freq_dict,idf_dict,req_book_df):
    tf_idf_score = {}
    for doc_id in list(req_book_df.index.values):
        tf_idf_score[doc_id] = {}
    for word in unique_words_list:
        for doc_id,doc in zip(list(req_book_df.index.values),req_book_df['combine']):
            tf_idf_score[doc_id][word] = term_freq_dict[doc_id][word] * idf_dict[word]
    return tf_idf_score

def search_engine_calc(req_book_df_clean_updt,unique_words_list):
    term_freq_dict = get_single_term_freq(unique_words_list,req_book_df_clean_updt)
    word_freq_dict = get_word_to_doc_freq(unique_words_list,req_book_df_clean_updt)
    idf_dict = get_idf(unique_words_list,word_freq_dict,req_book_df_clean_updt)
    tf_idf_score= calc_tfidf(unique_words_list,term_freq_dict,idf_dict,req_book_df_clean_updt)
    return tf_idf_score


def vectorSpaceModel(query, req_book_df,tf_idf_score):
    query_vocab = []
    for word in query.split():
        if word not in query_vocab:
            query_vocab.append(word)

    query_wc = {}
    for word in query_vocab:
        query_wc[word] = query.lower().split().count(word)

    
    relevance_scores = {}
    for doc_id in list(req_book_df.index.values):
        score = 0
        for word in query_vocab:
            try:
                score += query_wc[word] * tf_idf_score[doc_id][word]
            except KeyError:
                pass
        relevance_scores[doc_id] = score
    sorted_value = OrderedDict(sorted(relevance_scores.items(), key=lambda x: x[1], reverse = True))
    matched_doc = {k: sorted_value[k] for k in list(sorted_value)}
    return matched_doc