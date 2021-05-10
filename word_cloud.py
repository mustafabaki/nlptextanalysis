import matplotlib.pyplot as plt 
from wordcloud import WordCloud, STOPWORDS

import sys, os

def cloudify(filename):
    text = open("uploads/"+filename, mode='r', encoding='utf-8').read()
    stopwords = STOPWORDS

    wc = WordCloud(
        background_color = 'white',
        stopwords = stopwords,
        height=600,
        width = 400
    )
    wc.generate(text)

    out = "static/pics/"+filename+"_out.png"

    wc.to_file(out)



    