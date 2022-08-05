
from pickle import TRUE
from flask import Flask, render_template,render_template, request, url_for, flash, redirect
from crawler import cov_sefa_crawl
import srch_ngine_data 
import srch_ngine_core
app = Flask(__name__)
app.config['SECRET_KEY'] = 'df0331cefc6c2b9a5d0208a726a5d1c0fd37324feba25506'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/',methods=['POST'])
def getValue():
    title_val = request.form['title']
    check_val = request.form['check']

    if check_val == 'all_doc':
        whole_doc = True
    else:
        whole_doc = False

    # cov_sefa_crawl.crawling_main_page(whole_doc)
    req_book_df_clean_updt,unique_words_list = srch_ngine_data.initiate_data_process(whole_doc)
    tf_idf_score =srch_ngine_core.search_engine_calc(req_book_df_clean_updt,unique_words_list)
    matched_doc =srch_ngine_core.vectorSpaceModel(title_val,req_book_df_clean_updt,tf_idf_score)
    available_value_dict = [k for k,v in matched_doc.items() if v >0]
    # print('available_value_dict',available_value_dict)
    final_dict=dict()
    for a,b in enumerate(available_value_dict):
        a +=1
        title = req_book_df_clean_updt.loc[b]['doc_title']
        doc_link =req_book_df_clean_updt.loc[b]['book_link']
        authors = req_book_df_clean_updt.loc[b]['generic_authors']
        keywords =req_book_df_clean_updt.loc[b]['keywords']
        final_dict[a] =[title,doc_link,authors,keywords]
    # print(final_dict)

    return render_template('result.html',tt =title_val,ch=check_val,re=final_dict)

