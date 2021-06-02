# -*- coding: utf-8 -*-
"""nmf_with_user_data_en.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1p2MRygRq7_X0cNVmJO-1SMwOKGNC1t2p
"""

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF
import pandas as pd
import joblib
import re
import string
import spacy
from nltk.tokenize import word_tokenize
import nltk
pd.options.mode.chained_assignment = None  # default='warn'


#import user dataset
path='articles_small.csv' 
df = pd.read_csv(path)

column_name = 'text'
content = df[column_name]

#Cleaning Process

def clean_text(text):
    '''Make text lowercase, remove text in square brackets, remove punctuation and remove words containing numbers.'''
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    return text

i=0
for text in content:
  content[i]=clean_text(text)
  i=i+1

# Get N-number and Stopwords

#user's stopwords 
stopwords = []
a=False #if user does not give stopwords this variable = false
if a: 
  #kullanıcıdan gelen stopwordsleri split ile ayırıp for döngüsünde append ile stopwords listesine ekliyoruz.
  form="a,an,the,and,of,while,for,is,has,as,are,have,by,from,more,their" #example
  arr = form.split(',')
  for i in arr:
    stopwords.append(i)
else:
  sp = spacy.load('en_core_web_sm')
  stopwords = sp.Defaults.stop_words


#number of n
min_n_gram = 2
max_n_gram = 2 # user input

import nltk
nltk.download('punkt')
def stemmer_fun_stop(sentence,stopwords):
    token_words=word_tokenize(sentence)
    stem_sentence=[]
    for word in token_words:
      if word not in stopwords:
        stem_sentence.append(word)
        stem_sentence.append(" ") 
    return "".join(stem_sentence)

i=0
for text in content:
  content[i] = stemmer_fun_stop(text,stopwords)
  i=i+1

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
  lem_content = []
  sent = nltk.word_tokenize(sentence)
  for w in sent:
    word= lemmatizer.lemmatize(w, get_wordnet_pos(w))
    lem_content.append(word)
    lem_content.append(" ") 
  return "".join(lem_content)

i=0
for text in content:
  content[i] = lemma(text)
  i=i+1

# NMF is able to use tf-idf
tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=1000, ngram_range=(min_n_gram,max_n_gram)) 
tfidf = tfidf_vectorizer.fit_transform(content)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()
# Run NMF
nmf = NMF(n_components=20, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)

# To display words with desc. order 
def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print ("Topic %d:" % (topic_idx))
        print (" ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]))
        
no_top_words = 10
display_topics(nmf, tfidf_feature_names, no_top_words)

#Sample 
sample = """
  golf resorts lose a lot of money. According to a bombshell New York Times report published last year, the 15 courses he owns around the world have lost over $315 million over the past 20 years. The interesting question is why does Trump hang on to so many money-losing enterprises?
Much about Trump's financial arrangements remains a mystery — partly because privately listed companies in the US can largely avoid public scrutiny — though investigations into whether Trump committed bank and tax fraud may reveal more.
""" 
sample_clean = clean_text(sample)
sample_lem = stemmer_fun_stop(sample_clean,stopwords)
sample_all_clean = lemma(sample_lem)
# Transform the TF-IDF
test = tfidf_vectorizer.transform([sample_all_clean])
#  Transform the TF-IDF: nmf_features
nmf_features = nmf.transform(test)
 
 
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

#make list
def make_list(model, feature_names, no_top_words, topic_names , prct):
    lst = []
    y=19
    for x in range(5):
        topic_name = topic_names[0][y]
        y = y-1  
        for topic_idx, topic in enumerate(model.components_):
            if topic_name == topic_idx:
                lst.append( [prct[0][topic_name], " ".join([feature_names[i]
                                for i in topic.argsort()[:-no_top_words - 1:-1]])])
    return lst
    
no_top_words=10
prct = nmf.transform(test)*100
List = make_list(nmf, tfidf_feature_names, no_top_words, nmf.transform(test).argsort(axis=1), prct)

print(List)