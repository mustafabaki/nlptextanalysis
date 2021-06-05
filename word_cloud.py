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
    
    if shape  == 'a' : np.array(Image.open("2.jpg"))
    elif  shape == 'b' :  np.array(Image.open("3.jpg"))
    
    wc = WordCloud(
        background_color = 'white',
        stopwords = stopwords,
        height=600,
        width = 400,
        mask= shape
    )
    wc.generate(text)

    out = "static/pics/"+filename+"_out.png"

    wc.to_file(out)



