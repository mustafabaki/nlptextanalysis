# -*- coding: utf-8 -*-
"""NLPTR_WIKI_70.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12ndHORsf2cWi50CzOZN03CSqBxQ90p-7

# Import and Edit Data
"""

import pandas as pd

data = pd.read_csv('/content/drive/MyDrive/turkish_wikipedia_dump_20200401.csv')

data.head()

df=data['text']
df

"""# Import Necessary Libraries (some of them is optional)"""

import numpy as np
import nltk
import re
import warnings
from collections import Counter
import nltk
nltk.download('stopwords')
WPT = nltk.WordPunctTokenizer()
stop_word_list = nltk.corpus.stopwords.words('turkish')

!pip install gensim
import gensim
from gensim.utils import simple_preprocess
#from gensim.parsing.preprocessing import STOPWORDS           #Does not support Turkish yet.
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
np.random.seed(400)

nltk.download('wordnet')

"""**Checking Stemmer**"""

import pandas as pd
from snowballstemmer import TurkishStemmer
stemmer=TurkishStemmer()
original_words = ['Başarılı', 'insanlar', 'adamlar', 'öldüler', 'içindekiler','kapısındaki', 'yiyecekler,', 'çıkaranlar', 
           'lahanalar', 'takımların','sırası', 'futbolcuların', 'yedikleri']
singles = [stemmer.stemWord(plural) for plural in original_words]

pd.DataFrame(data={'original word':original_words, 'stemmed':singles })

"""**Stemming and Tokenizing Functions**"""

def lemmatize_stemming(text):       # Lemmetizing is removed because it is not appropriate for turkish
    return stemmer.stemWord(text)

# Tokenize and lemmatize
def preprocess(text):
    result=[]
    for token in gensim.utils.simple_preprocess(text) :
        if token not in stop_word_list and len(token) > 3:
            result.append(lemmatize_stemming(token))
     
    return result

"""**Testing Functions**"""

doc_sample = 'Bu disk çok fazla kez hata verdi. Mümkünse bunu başka bir tane ile değiştirmek istiyorum.'

print("Original document: ")
words = []
for word in doc_sample.split(' '):
    words.append(word)
print(words)
print("\n\nTokenized and stemmed document: ")
print(preprocess(doc_sample))

"""# Clean the Data"""

import pprint
data['text'].fillna('').astype(str)
df=data['text']
df.astype(str)
print(df)
df = df.astype(str) 
df = df.map(lambda x: re.sub('[,\.!?();:$%&#"]', '', x))
df = df.replace('\n','', regex=True)                     # depends on the data
df = df.replace('\'','', regex=True)                     # depends on the data
df = df.replace('-','', regex=True)                      # depends on the data
df = df.replace('’','', regex=True)                      # depends on the data
df[0]

"""**Tokenizing and Stemming the Original Data**"""

processed_docs = []
!pip install progressbar2
from progressbar import ProgressBar
bar = ProgressBar()

for doc in bar(abc):
    processed_docs.append(preprocess(doc))

"""# Adding to the Dictionary"""

dictionary = gensim.corpora.Dictionary(processed_docs)

count = 0                         #Testing if it is created
for k, v in dictionary.iteritems():
    print(k, v)
    count += 1
    if count > 10:
        break

'''
Remove very rare and very common words: (Probably not working for Turkish but I tried)
'''
dictionary.filter_extremes(no_below=15, no_above=0.1, keep_n= 100000)

'''
Create the Bag-of-words model for each document i.e for each document we create a dictionary reporting how many
words and how many times those words appear. Save this to 'bow_corpus'
'''
bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

'''
Preview BOW for our sample preprocessed document
'''
document_num = 20
bow_doc_x = bow_corpus[document_num]

for i in range(len(bow_doc_x)):
    print("Word {} (\"{}\") appears {} time.".format(bow_doc_x[i][0], 
                                                     dictionary[bow_doc_x[i][0]], 
                                                     bow_doc_x[i][1]))

"""**Saving**"""

import pickle
pickle.dump(bow_corpus, open('corpus.pkl', 'wb'))
dictionary.save('dictionary.gensim')

"""# LDA Model"""

lda_model =  gensim.models.LdaMulticore(bow_corpus, 
                                   num_topics = 70, 
                                   id2word = dictionary,                                    
                                   passes = 10,
                                   workers = 2)

'''
For each topic, we will explore the words occuring in that topic and its relative weight
'''
for idx, topic in lda_model.print_topics(-1):
    print("Topic: {} \nWords: {}".format(idx, topic ))
    print("\n")
lda_model.save('model_70_topic.gensim')               #Saving the model

"""# Testing with Unseen Sentence"""

unseen_document = "linux"
print(unseen_document)

# Data preprocessing step for the unseen document
bow_vector = dictionary.doc2bow(preprocess(unseen_document))

for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
    print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))

"""**Note: Do not forget to clean the sentence entered. This was a test, so I did not add punctuations.**"""