# -*- coding: utf-8 -*-
"""nmf_ready_to_use.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AvZHoK24WsDf0diEkzfYRFbPb8vmRR5H
"""
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF
import pandas as pd
pd.set_option('display.max_columns', None)  
pd.set_option('display.max_colwidth', None)
#import data
df = pd.read_csv('NMF_clean_data.csv')

content = df['0']

# clean the data
"""run just ones to install en_core_web_sm, if you don't have it"""
# !python -m spacy download en_core_web_sm 

import spacy
import re
import string
def clean_text(text):
    '''Make text lowercase, remove text in square brackets, remove punctuation and remove words containing numbers.'''
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    return text

nlp = spacy.load("en_core_web_sm")
def lemmatizer(text):        
    sent = []
    doc = nlp(text)
    for word in doc:
        sent.append(word.lemma_)
    return " ".join(sent)

# NMF is able to use tf-idf
tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words='english')
# tfidf = tfidf_vectorizer.fit_transform(df_clean)
tfidf = tfidf_vectorizer.fit_transform(content)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()

# Run NMF
nmf = NMF(n_components=30, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)

# To display words with desc. order 
def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print ("Topic %d:" % (topic_idx))
        print (" ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]))
        
no_top_words = 10
#display_topics(nmf, tfidf_feature_names, no_top_words)

import pandas as pd

#Sample 
sample = """
  golf resorts lose a lot of money. According to a bombshell New York Times report published last year, the 15 courses he owns around the world have lost over $315 million over the past 20 years. The interesting question is why does Trump hang on to so many money-losing enterprises?
Much about Trump's financial arrangements remains a mystery — partly because privately listed companies in the US can largely avoid public scrutiny — though investigations into whether Trump committed bank and tax fraud may reveal more.
""" 
sample_clean = clean_text(sample)
sample_lem = lemmatizer(sample_clean)
sample_all_clean = sample_lem.replace('-PRON-', '')

# Transform the TF-IDF
test = tfidf_vectorizer.transform([sample_all_clean])
#  Transform the TF-IDF: nmf_features
nmf_features = nmf.transform(test)
 

def display_topic_of_sample(model, feature_names, no_top_words, topic_name):
    for topic_idx, topic in enumerate(model.components_):
      if topic_name==topic_idx:
        print ("Topic %d:" % (topic_idx))
        print (" ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]))

#display_topic_of_sample(nmf, tfidf_feature_names, no_top_words, nmf.transform(test).argmax(axis=1))

def display_topics_of_sample(model, feature_names, no_top_words, topic_names , prct):
  y=29
  for x in range(5):
    topic_name = topic_names[0][y]
    y = y-1  
    for topic_idx, topic in enumerate(model.components_):
      if topic_name == topic_idx:
        print ("Topic percentage %" , prct[0][topic_name])
        print (" ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]))

prct = nmf.transform(test)*100
#display_topics_of_sample(nmf, tfidf_feature_names, no_top_words, nmf.transform(test).argsort(axis=1), prct)

#make list
def make_list(model, feature_names, no_top_words, topic_names , prct):
    lst = []
    y=29
    for x in range(5):
        topic_name = topic_names[0][y]
        y = y-1  
        for topic_idx, topic in enumerate(model.components_):
            if topic_name == topic_idx:
                lst.append( [prct[0][topic_name], " ".join([feature_names[i]
                                for i in topic.argsort()[:-no_top_words - 1:-1]])])
    return lst
prct = nmf.transform(test)*100
List = make_list(nmf, tfidf_feature_names, no_top_words, nmf.transform(test).argsort(axis=1), prct)

print(List)
