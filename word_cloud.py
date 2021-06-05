from flask.wrappers import Request
import matplotlib.pyplot as plt 
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import numpy as np
from flask import request
import sys, os

def cloudify(filename , shape):
    text = open("uploads/"+filename, mode='r', encoding='utf-8').read()
    stopwords = STOPWORDS
    
    if shape  == 'a' : 
        mask =  np.array(Image.open("2.jpg")) #added mask variable to use below
    elif  shape == 'b' :  
        mask  = np.array(Image.open("3.jpg"))
    
    wc = WordCloud(
        background_color = 'white',
        stopwords = stopwords,
        height=mask.shape[0],
        width=mask.shape[1],
        mask= mask # mask variable is used here...
    )
    wc.generate(text)

    out = "static/pics/"+filename+"_out.png"

    wc.to_file(out)



