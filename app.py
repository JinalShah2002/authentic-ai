"""

@author: Jinal Shah

This script is for the webpage
front-end for this project.

The front-end will be simple with the following 
feature:

A text box for a user to enter text to be fed into 
the model. 

"""
# Importing libraries
import re
import streamlit as st 
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn as nn

st.markdown("<h1 style='text-align: center; color: teal;'>Verify.AI</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: teal;'>Using machine learning to detect A.I generated essays 🤖</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: teal;'>How It Works</h3>", unsafe_allow_html=True)
st.write('Paste your essay into the below text box and click submit. Within 3 minutes, you will see a probability of how likely your essay is generated by A.I')

# a function for preprocessing 
def preprocess(essay:str):
    preprocessed_essay = essay.lower()
    
    # Subbing out \n and \t
    preprocessed_essay = re.sub("\n","",preprocessed_essay)
    preprocessed_essay = re.sub("\t","",preprocessed_essay)

    # Replacing /xa0 = non-breaking space in Latin1
    preprocessed_essay = preprocessed_essay.replace(u'\xa0', u' ')
    
    return preprocessed_essay

# Getting the tokenizer and model
@st.cache_resource
def get_all():
    tokenizer = AutoTokenizer.from_pretrained("JinalShah2002/distilbert-detector")
    model = AutoModelForSequenceClassification.from_pretrained("JinalShah2002/distilbert-detector")
    return tokenizer, model

# Defining a function for inference
def inference(essay,tokenize,language_model):
    # Tokenizing the input essay
    inputs = tokenize(essay,padding='max_length',truncation=True,max_length=512,return_tensors='pt')
    
    # Getting the logits
    with torch.no_grad():
        logits = language_model(**inputs).logits
        probability = nn.functional.sigmoid(logits)
    return probability

# Creating state for inputted essay
if 'essay' not in st.session_state.keys():
    st.session_state['essay'] = ''

# Getting the tokenizer and the model
tokenizer,model = get_all()

# Creating a form to drop the text into 
form = st.form(key='my_form')

# Need to make sure the \n are recognized as escape characters
st.session_state['text'] = form.text_area(label='Enter the Essay:').replace(r'\n','\n').replace(r'\xa0','\xa0').replace(r'\t','\t')
submit_button = form.form_submit_button('Submit')

# If button clicked
if submit_button:
    # Sending text through the preprocessing pipeline
    preprocessed_essay = preprocess(st.session_state['text'])

    # Getting the probability
    probability = inference(preprocessed_essay,tokenizer,model)

    # Decision Boundary (Boundary is 71% or 0.71)
    if probability > 0.71:
        st.markdown("<p style='text-align: center; color: red;'>LLM Written</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align: center; color: green;'>Not LLM Written</p>", unsafe_allow_html=True)
    st.write("Note: this is simply a prediction. It can be incorrect ,and one shouldn't use this detector as a primary means of determining essay authorship! False Positives are possible!")