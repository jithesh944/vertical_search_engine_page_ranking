import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import numpy as np
from lxml import etree
from urllib.parse import urljoin
from time import sleep
import schedule


def get_soup_object(rel_path,print_cond = False):
    base_path = r'https://pureportal.coventry.ac.uk'
    initial_path = urljoin(base_path,rel_path)
    
    main_html_page = requests.get(initial_path)
    if main_html_page.status_code == 200:
        generic_soup_obj = BeautifulSoup(main_html_page.content,'html.parser')
    else:
        print("Main page not avaialble.")
        return "No object"
    if print_cond:
        print('initial_path',initial_path)
        print(generic_soup_obj.prettify())
    return generic_soup_obj


def get_page_link(SFEA_main_obj,class_name,whole_doc = True):
    main_tags = SFEA_main_obj.find_all('div',class_=class_name)
    a_tag= main_tags[0].find_all('a',class_='portal_link btn-primary btn-large')
    link = a_tag[0]['href']
    if  (class_name =='organisation-publications' and whole_doc == False):
        filter_div = SFEA_main_obj.find('div',class_='content-trends')
        filter_tag_ul = filter_div.find('ul',class_="content-statistics")
        filter_tag_li = filter_tag_ul.find_all("a")
        link=list()
        for indi_tag_li in filter_tag_li:
            if (indi_tag_li.find('span').text.strip() in ['17 Book','49']):
                link.append(indi_tag_li['href'])
    return link

def get_persons_links(person_profile_link):
    
    next_page_present = True
    profiles_data = dict()
    while(next_page_present):
        person_profile_page_obj = get_soup_object(person_profile_link)
        person_profile_pagination = person_profile_page_obj.find('nav',class_='pages')
        person_profile_pagination_list = person_profile_pagination.find_all('li')

        person_profile_details = person_profile_page_obj.find('ul',class_='grid-results')
        te = person_profile_details.find_all('a',class_='link person')

        for i in range(len(te)):
            profiles_data[te[i].text] = te[i]['href']
            
        if person_profile_pagination_list[-1].text != 'Next ›':
            next_page_present  = False
        else:
            new_pfile_link= person_profile_pagination_list[-1].find('a')
            person_profile_link = new_pfile_link['href']
            
    return profiles_data


def get_publications_links(org_publications_links):
    publications_data = dict()
    last_book_num = 0
    for org_publications_link in org_publications_links:
        next_page_present = True
        while(next_page_present):
            publication_page_obj = get_soup_object(org_publications_link)
            publication_pagination = publication_page_obj.find('nav',class_='pages')
            publication_pagination_list = publication_pagination.find_all('li')
            publication_details = publication_page_obj.find('ul',class_='list-results')
            li_tags = publication_details.find_all('li',class_='list-result-item')
            book_data= dict()
            for i,li_tag in enumerate(li_tags):
                i = last_book_num + i
                li_h3_tags = li_tag.find_next('h3')
                doc_header = li_h3_tags.text
                doc_link = li_h3_tags.find('a')['href']
                key = 'book_' +str(i)
                book_data[key] = [doc_header,doc_link]
            last_book_num = i + 1
            try:
                if publication_pagination_list[-1].text != 'Next ›':
                    next_page_present  = False
                else:
                    new_publication_link= publication_pagination_list[-1].find('a')
                    org_publications_link = new_publication_link['href']
            except IndexError:
                next_page_present  = False
                
            publications_data.update(book_data)
#     print(publications_data)
        
    return (publications_data)

def get_publication_details(publications_data):

    publication_data = dict()
    
    for doc_num, doc_data in publications_data.items():
        if doc_num in ['book_100','book_200','book_300''book_400','book_500','book_600']:
            sleep(0.05)
        
        book_page = get_soup_object(doc_data[1])
        book = dict()
        book['doc_id'] = doc_num
        book['doc_title'] = doc_data[0]
        book["book_link"] =doc_data[1]
        
#         getting all authors and coventry authors
        book_section_tag = book_page.find('section',class_='page-section-header-publications-view')
        book_authors_list = book_section_tag.find('p',class_ ='relations persons')
        generic_book_authors = book_authors_list.get_text().split(',')
        book['generic_authors'] =generic_book_authors
        coventry_author_data = dict()
        for val in book_authors_list.find_all('a'):
            coventry_author= val.text
            coventry_author_link = val['href']
            coventry_author_data[coventry_author] = coventry_author_link
        book['coventry_authors'] = coventry_author_data

        
#         Get all other details (abstract)
        try:
            book_detail_tag = book_page.find('div',class_='textblock')
            book_abstract_text = book_detail_tag.text
        except:
            book_abstract_text = ''
        book['abstract'] = book_abstract_text
        
#         Getting all properties values
        book_properties_table =book_page.find('table',class_='properties')
        book_properties_table_body = book_properties_table.find('tbody')
        table_rows = book_properties_table_body.find_all('tr')
        book_properties_dict =dict()
        for row in table_rows:
            cols = row.find_all(['th','td'])
            book_properties_dict[(cols[0].text)] = cols[1].text
        book['published_on'] = book_properties_dict['Publication status'].split('- ')[1]

#         get the main keywords
        try: 
            book_keywords_ul = book_page.find('ul',class_='relations keywords')
            book_keywords_li = book_keywords_ul.find_all('li')
            keyword = list()
            for word in book_keywords_li:
                keyword.append(word.text)
        except:
            keyword =['No keywords']
            
        book['keywords'] = keyword
        
#         Appending dict to final dict
        publication_data[doc_num] = book
    
    return publication_data

def crawling_main_page(whole_doc):
    SFEA_main_obj = get_soup_object('/en/organisations/school-of-economics-finance-and-accounting')
    person_profile_link = get_page_link(SFEA_main_obj,"organisation-persons")
    org_publications_links = get_page_link(SFEA_main_obj,'organisation-publications',whole_doc)
   
    profiles_data = get_persons_links(person_profile_link)
    publications_data = get_publications_links(org_publications_links)
#     print(publications_data)
#     publications_data = test_data
    publications_details = get_publication_details(publications_data)
    book_df = pd.DataFrame.from_dict(publications_details,orient='index')
#     print(book_df.head())
    book_df_test.to_csv('Publications_dump.csv', encoding='utf-8',sep=',')
    return book_df
#     print(publications_data)
#     return 'succes'


if __name__=='__main__':
    whole_doc = False
    book_df_test = schedule.every().monday.do(crawling_main_page(whole_doc))
