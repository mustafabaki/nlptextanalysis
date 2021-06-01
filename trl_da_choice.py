def make_ngrams(texts,n,ngram_mod):
    return [turnmod(doc,n,ngram_mod) for doc in texts]

def lemmatization(texts, allowed_postags=["Noun", 'Adj', 'Verb', 'Adv']):
      texts_out = []
      for sent in texts:
          x=analyzer.analyze(sent)[0][0]
          if (x.pos=="Unk"):
            texts_out.append(analyzer.lemmatize(sent)[0][1][0])
          else:
            texts_out.append(x.lemma)
      return texts_out



def clean(df):
  df.fillna('').astype(str)
  df=df.astype(str)
  df = df.map(lambda x: re.sub('[,\.!?();:$%&#"]', '', x))
  df = df.replace('\n','', regex=True)                     # depends on the data
  df = df.replace('\'','', regex=True)                     # depends on the data
  df = df.replace('-','', regex=True)                      # depends on the data
  df = df.replace('’','', regex=True)
  return df 

def prepare_stopwords(link='C:/Users/akdem/Desktop/nlptextanalysis-main/stopwords.csv'):
  stop_word_list=pd.read_csv(link)
  stop_word_list=stop_word_list.values.tolist()
  stopwords=[]
  for i in stop_word_list:
    stopwords.append(i[0])
  return stopwords

from multiprocessing import Process, freeze_support
import pandas as pd
import pickle
import zeyrek
import nltk
#nltk.download('punkt')
analyzer = zeyrek.MorphAnalyzer()
import numpy as np
import nltk
import re
import warnings
from collections import Counter
import nltk
import gensim
from gensim.utils import simple_preprocess
#from gensim.parsing.preprocessing import STOPWORDS           #Does not support Turkish yet.
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *
import numpy as np





def f():
    open_file = open("C:/Users/akdem/Desktop/nlptextanalysis-main/test.pkl", "rb")
    loaded_list = pickle.load(open_file)
    open_file.close()
    df=loaded_list


    print('hello world!')
    ######################################################################
    if (False):
        stopwords=prepare_stopwords('FILE NAME')
    else:
        stopwords=prepare_stopwords()
    ######################################################################
    print("stop bitti")
    df=clean(df)
    print("clean bitti")
    processed_docs = []

    for doc in df:
        processed_docs.append(preprocess(doc,stopwords))
    ############################################################################
    if True:
        ngram=[]
        ngram_mod=[]
        for i in range(3):
            if(i==0):
                ngram.append(gensim.models.Phrases(processed_docs[0:10000], min_count=5, threshold=100)) # higher threshold fewer phrases
            else:
                ngram.append(gensim.models.Phrases(ngram[i-1][processed_docs[0:10000]], min_count=5, threshold=100)) # higher threshold fewer phrases
            ngram_mod.append(gensim.models.phrases.Phraser(ngram[i]))
    
    ###########################################################################

    ################################################################################
    if True:
    # Form Ngrams
        data_words_ngrams = make_ngrams(processed_docs,3,ngram_mod)
        print("ngram bitti")
        # Do lemmatization keeping only noun, adj, vb, adv
        data_lemmatized=[]
        for i in range(len(data_words_ngrams)):
            data_lemmatized.append(lemmatization(data_words_ngrams[i], allowed_postags=['Noun', 'Adj', 'Verb', 'Adv']))
    else:
        data_lemmatized=processed_docs
    ################################################################################
    print("lemmatize bitti")

    dictionary = gensim.corpora.Dictionary(data_lemmatized)
    print("a")
    dictionary.filter_extremes(no_below=2, no_above=0.2, keep_n= 100000)
    print("b")
    bow_corpus = [dictionary.doc2bow(doc) for doc in data_lemmatized]
    print("c")
    lda_model =  gensim.models.LdaMulticore(bow_corpus, 
                                   num_topics = 70, 
                                   id2word = dictionary,                                    
                                   passes = 10, workers = 2)
    print("lda bitti")
    for idx, topic in lda_model.print_topics(-1):
        print("Topic: {} \nWords: {}".format(idx, topic ))
        print("\n")
    lda_model.save('turk_lda.gensim')

    unseen_document = "Çin Cengiz Han"
    print(unseen_document)

    # Data preprocessing step for the unseen document
    bow_vector = dictionary.doc2bow(preprocess(unseen_document,stopwords))

    for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
        print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))

def turnmod(text,n,ngram_mod):
    data_gram=ngram_mod[0][text]
    for i in range(n-1):
      data_gram=ngram_mod[i+1][data_gram]
    return data_gram

def preprocess(text,stopwords):
    result=[]
    for token in gensim.utils.simple_preprocess(text) :
        if token not in stopwords and len(token) > 3:
            result.append(token)
     
    return result

if __name__ == '__main__':
    freeze_support()
    Process(target=f).start()

