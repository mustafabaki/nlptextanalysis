class result:
    """
    holds topic names and their proportions
    """
    def __init__(self, topic, score):
        self.topic = topic
        self.score = score


def make_ngrams(texts,n,ngram_mod):
    """
    sends each text to turmod function and returns its outputs as a list
    """
    return [turnmod(doc,n,ngram_mod) for doc in texts]

def lemmatization(texts):
    """
    Checks each word, make them lemmatized and returns lemmatized words as strings
    """
      texts_out = []
      for sent in texts:
          x=analyzer.analyze(sent)[0][0]
          if (x.pos=="Unk"):
            texts_out.append(analyzer.lemmatize(sent)[0][1][0])
          else:
            texts_out.append(x.lemma)
      return texts_out



def clean(df):
    """
    Cleans the data from some noisy elements (it can be change according to the data sent)
    """
  df.fillna('').astype(str)
  df=df.astype(str)
  df = df.map(lambda x: re.sub('[,\.!?();:$%&#"]', '', x))
  df = df.replace('\n','', regex=True)                     # depends on the data
  df = df.replace('\'','', regex=True)                     # depends on the data
  df = df.replace('-','', regex=True)                      # depends on the data
  df = df.replace('’','', regex=True)
  return df 

def prepare_stopwords(link):
    """
    Creates stopword list. If there is no specialized stopwors, then it uses default document.
    """"
  stop_word_list=pd.read_csv(link)
  stop_word_list=stop_word_list.values.tolist()
  stopwords=[]
  for i in stop_word_list:
    stopwords.append(i[0])
  return stopwords

from multiprocessing import Process, freeze_support, Queue
from multiprocessing.queues import Queue
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





def f(DATA_LINK, DATA_COLUMN_NAME, STOPWORD_CHOICE, STOPWORD_LINK, NGRAM_CHOICE,NGRAM_NUM, TestData,topic_number_user,fetchArray):
    """
    Main function to be called in interface
    """
    data = pd.read_csv(DATA_LINK)
    df=data[DATA_COLUMN_NAME]
    ######################################################################
    if (STOPWORD_CHOICE):
        stopwords=prepare_stopwords(STOPWORD_LINK)
    else:
        stopwords=prepare_stopwords(link='stopwords.csv')
    ######################################################################

    df=clean(df)

    processed_docs = []

    for doc in df:
        processed_docs.append(preprocess(doc,stopwords))
    ############################################################################
    if NGRAM_CHOICE:
        ngram=[]
        ngram_mod=[]
        for i in range(NGRAM_NUM):
            if(i==0):
                ngram.append(gensim.models.Phrases(processed_docs[0:10000], min_count=5, threshold=100)) # higher threshold fewer phrases
            else:
                ngram.append(gensim.models.Phrases(ngram[i-1][processed_docs[0:10000]], min_count=5, threshold=100)) # higher threshold fewer phrases
            ngram_mod.append(gensim.models.phrases.Phraser(ngram[i]))
    
    ###########################################################################

    ################################################################################
    if NGRAM_CHOICE:
    # Form Ngrams
        data_words_ngrams = make_ngrams(processed_docs,NGRAM_NUM,ngram_mod)

        # Do lemmatization keeping only noun, adj, vb, adv
        data_lemmatized=[]
        for i in range(len(data_words_ngrams)):
            data_lemmatized.append(lemmatization(data_words_ngrams[i]))
    else:
        data_lemmatized=processed_docs
    ################################################################################
  

    dictionary = gensim.corpora.Dictionary(data_lemmatized)

    dictionary.filter_extremes(no_below=15, no_above=0.1, keep_n= 100000)

    bow_corpus = [dictionary.doc2bow(doc) for doc in data_lemmatized]

    lda_model =  gensim.models.LdaMulticore(bow_corpus, 
                                   num_topics = topic_number_user, 
                                   id2word = dictionary,                                    
                                   passes = 10, workers = 2)

    for idx, topic in lda_model.print_topics(-1):
        print("Topic: {} \nWords: {}".format(idx, topic ))
        print("\n")
    lda_model.save('turk_lda.gensim')

    unseen_document = TestData

    rx = re.compile('\W+')
    unseen_document = rx.sub(' ', unseen_document).strip()


    # Data preprocessing step for the unseen document
    bow_vector = dictionary.doc2bow(preprocess(unseen_document,stopwords))

    topics = []
    for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1*tup[1]):
      print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))
      # rslt = result(str(score), str(lda.print_topic(index,5)))
      rslt = result(str(score), str(re.findall('"([^"]*)"', str(lda_model.print_topic(index,5)))))
      topics.append(rslt)

    fetchArray.put(topics)

def turnmod(text,n,ngram_mod):
    """
    Completes ngrams cumulatively according to the amount of given ngrams
    """
    data_gram=ngram_mod[0][text]
    for i in range(n-1):
      data_gram=ngram_mod[i+1][data_gram]
    return data_gram

def preprocess(text,stopwords):
    """
    Filters the words according to stopwords and their length.
    """
    result=[]
    for token in gensim.utils.simple_preprocess(text) :
        if token not in stopwords and len(token) > 3:
            result.append(token)
     
    return result



