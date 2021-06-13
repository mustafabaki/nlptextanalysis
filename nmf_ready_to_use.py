# -*- coding: utf-8 -*-
"""nmf_fast.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OwSYcDVUm-QI9Euat9O00KtHst_QL_v1
"""

"""This class is an auxilary class to pass the results to web app. """
class result:
    def __init__(self, topic, score):
        self.topic = topic
        self.score = score

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

import nltk
nltk.download('punkt')
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF
import pandas as pd
import joblib
from nltk.tokenize import word_tokenize
import nltk
#!python -m spacy download en_core_web_sm #run just ones to install en_core_web_sm, if you don't have it
sp = spacy.load('en_core_web_sm')
stopwords = sp.Defaults.stop_words

def stemmer_fun_stop(sentence,stopwords):
    """
    remove the stopwords from the sentence
    """
    token_words=word_tokenize(sentence)
    stem_sentence=[]
    for word in token_words:
        if word not in stopwords:
            stem_sentence.append(word)
            stem_sentence.append(" ") 
    return "".join(stem_sentence)

import nltk
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)

def lemma(sentence):
    """
    lemmatize the given sentence
    """
    lem_content = []
    sent = nltk.word_tokenize(sentence)
    for w in sent:
        word= lemmatizer.lemmatize(w, get_wordnet_pos(w))
        lem_content.append(word)
        lem_content.append(" ") 
    return "".join(lem_content)

#make list
def make_list(model, feature_names, no_top_words, topic_names , prct):
    """
    return list of most used words with topics
    """
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

def nmf_algorithm(thetext,ngram_num):
  """
  thetext is the sample text which will be analyzed. ngram_num is the n gram number
  """
  
  pd.set_option('display.max_columns', None)  
  pd.set_option('display.max_colwidth', None)
  #import data
  df = pd.read_csv('Algorithm/NMF/NMF_clean_data.csv')
  content = df['0']

  import joblib
  from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
  
  n_gram = ngram_num #ngram_number

  no_top_words = 10
  # NMF is able to use tf-idf
  tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=1000, stop_words='english', ngram_range=(n_gram,n_gram))
  tfidf = tfidf_vectorizer.fit_transform(content)

  if n_gram == 1:
    tfidf_feature_names = joblib.load('Algorithm/NMF/tfidf_feature_names_1gram.sav')
    nmf = joblib.load('Algorithm/NMF/finalized_model_1gram.sav')
  elif n_gram == 2:
    tfidf_feature_names=joblib.load('Algorithm/NMF/tfidf_feature_names_2gram.sav')
    nmf = joblib.load('Algorithm/NMF/finalized_model_2gram.sav')
  elif n_gram == 3:    
    tfidf_feature_names = joblib.load('Algorithm/NMF/tfidf_feature_names_3gram.sav')
    nmf = joblib.load('Algorithm/NMF/finalized_model_3gram.sav')
      
  import pandas as pd

  #Sample 
  sample = thetext
  sample_clean = clean_text(sample)
  sample_lem = stemmer_fun_stop(sample_clean,stopwords)
  sample_all_clean = lemma(sample_lem)

  # Transform the TF-IDF
  test = tfidf_vectorizer.transform([sample_all_clean])
  #  Transform the TF-IDF: nmf_features
  nmf_features = nmf.transform(test)
  
  prct = nmf.transform(test)*100
  List = make_list(nmf, tfidf_feature_names, no_top_words, nmf.transform(test).argsort(axis=1), prct)

  rslt = []
  print(List)
  print(len(List))
  for index in range(len(List)):
    theresult = result(List[index][1], List[index][0])
    rslt.append(theresult)
  
  return rslt
    
    
    
