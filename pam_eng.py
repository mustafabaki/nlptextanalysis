import sys
import tomotopy as tp


def pam_english(input_file):
    """ 
    This function runs PAM algorithm for the specified English text, extracts n-grams, returns topics with subtopics of the text file.
    """
    print("importing...")
    from nltk.stem.porter import PorterStemmer
    from nltk.corpus import stopwords
    
    stemmer = PorterStemmer()
    stops = set(stopwords.words('english'))

    train_corpus = tp.utils.Corpus(tokenizer=tp.utils.SimpleTokenizer(stemmer=stemmer.stem),
                                   stopwords=lambda x: len(x) <= 2 or x in stops)

    # data_feeder yields a tuple of (raw string, user data) or a str (raw string)
    train_corpus.process(open(input_file, encoding='utf-8'))
    # make PA model and train
    print("training model...")
    mdl = tp.PAModel(k1=5, k2=5, min_cf=2, min_df=1, corpus=train_corpus)

    for i in range(0, 250, 10):  # increase 100 for more accurate results, but it will take more time
        mdl.train(10)
        print('Iteration: {}\tLog-likelihood: {}'.format(i, mdl.ll_per_word))

    # mdl.summary()
    # save pam for reuse
    mdl.save('trained_pam.bin')
    # for loading use mdl.load('trained_pam.bin')

    # Creating ngrams, max_len determines bigram or trigram, 3 means trigram
    ngrams = train_corpus.extract_ngrams(min_cf=2, max_len=3)
    for c in ngrams:
        if len(c.words) == 3:
            print(c.words[0], c.words[1], c.words[2], sep='\t') # ngram words

    topic_result = []
    for k in range(mdl.k1):
        print("== Topic #{} ==".format(k))
        subs = []
        subs_prob = []
        sub_topics = mdl.get_sub_topics(k, top_n=5)
        for subtopic, probability in sub_topics:
            for word, p in mdl.get_topic_words(subtopic, top_n=1):
                subs.append(word)
            subs_prob.append(probability)
        for word, prob in mdl.get_topic_words(k, top_n=1):
            topic_result.append({"topic": word, "prob": prob, "subs": subs, "subs_prob": subs_prob})

    return topic_result


# print('Running PAM from raw corpus')
# topics = pam_english('enwiki-1000.txt')
# example for accessing values
# topic represents main topic, prob represents probability of main topic
# subs represents list of 5 sub topics
# subs_prob represents list 5 sub topics probabilities
# first element of subs_prob corresponds to first element of subs
# probabilities for the main topics are unsorted
# for w in range(len(topics)):
   # print("\n")
   # print(topics[w]["topic"], topics[w]["prob"], topics[w]["subs"], topics[w]["subs_prob"], sep='\t')
