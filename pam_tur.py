import sys
import tomotopy as tp


def pam_turkish(input_file):
    print("importing...")
    from snowballstemmer import TurkishStemmer
    from nltk.corpus import stopwords
    stemmer = TurkishStemmer()
    stops = set(stopwords.words('turkish'))
    print("preparing corpus...")
    train_corpus = tp.utils.Corpus(tokenizer=tp.utils.SimpleTokenizer(stemmer=stemmer._stem()),
                                   stopwords=lambda x: len(x) <= 2 or x in stops)

    # data_feeder yields a tuple of (raw string, user data) or a str (raw string)
    train_corpus.process(open(input_file, encoding='utf-8'))

    # make PA model and train
    print("training model...")
    mdl = tp.PAModel(k1=5, k2=25, min_cf=10, min_df=1, corpus=train_corpus, seed=42)
    for i in range(0, 100, 10):  # increase 100 for more accurate results, but it will take more time
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
            print(c.words[0], c.words[1], c.words[2], sep='\t')  # ngram words
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
            print(word, prob, sep='\t')
            topic_result.append({"topic": word, "prob": prob, "subs": subs, "subs_prob": subs_prob})

    return topic_result

# example usage
# topics = pam_turkish('tolstoy.txt')
