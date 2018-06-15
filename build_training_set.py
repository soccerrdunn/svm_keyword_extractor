# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 16:47:32 2018

@author: OGPUser
"""
import re, itertools, csv
import numpy as np
import pandas as pd
from nltk.tokenize import RegexpTokenizer

fi = open('C:\\Users\\OGPUser\\py_proj\\sem_eval2010\\train\\train.combined.final', 'r', encoding='utf8')
X=[]
Y=[]

#myline = "C-41 : adaptive resource management,distributed real-time embedded system,end-to-end quality of service+service end-to-end quality,hybrid adaptive resourcemanagement middleware,hybrid control technique,real-time video distribution system,real-time corba specification,video encoding/decoding,resource reservation mechanism,dynamic environment,streaming service"
#doc_id = re.match(r'[CHJI]\-\d\d', myline).group()
#doc_id = re.search(r'([CHJI]\-\d\d) : (.{1,})', myline)

#setup what you are going to tokenize your words by in your keyword training set
#in our case we're going to ignore the + because we're ignoring reciprical words
#may need to re-consider if you start to search through phrases as all of these
# are focused only on single words, if phrases, only tokenize on commas
tokenizer = RegexpTokenizer('[\+^]| |,', gaps=True)

#for each line in the training set file
for line in fi:

    #From the train results file grab all of the words, the first word which 
    #will be in line_contents.group(1) will be the document ID, i.e. what will
    #need to be opened subsequently as the text. 
    line_contents = re.search(r'([CHJI]\-\d\d) : (.{1,})', line)
    
    print(line_contents.group(1))
    print('\n')
    #separate out your words
    mywords=set(tokenizer.tokenize(line))

    #open up the base document and read in the text
    fpath = 'C:\\Users\\OGPUser\\py_proj\\sem_eval2010\\train\\' + line_contents.group(1) + '.txt.final'
    base_file = open(fpath, 'r', encoding='utf8')
    doc_text = base_file.read()    
    base_file.close()

    # get a list of candidate words, best way is to use textrank algorithm and 
    #grab as many words as you can, this will ignore the stop words, a, the, etc
    candidates = score_keyphrases_by_textrank(doc_text,.99,2)
    candidate_words = [x[0]for x in candidates]
    #good words are intersection with mywords and candidates
    good_words=mywords.intersection(candidate_words)
    candidate_words=candidate_words[0:45]#limit to 45 words and then recombine
    total_words = set(good_words) | set(candidate_words)
    
    x=[0,0,0,0,0,0]
    for candidate in total_words:
        #get the feature vector
        word_features=extract_candidate_features(candidate, doc_text)
        
        x=[word_features[candidate]['term_count'],
           word_features[candidate]['term_length'],
           word_features[candidate]['spread'],
           word_features[candidate]['abs_first_occurrence'],
           word_features[candidate]['abs_last_occurrence'],
           word_features[candidate]['text_rank'],]
        
        if candidate in good_words:
            y=1
        else:
            y=-1
        
        X.append(x)
        Y.append(y)
        
#convert the list to matrices & arrays, send to SVMrank to learn, and VIOALA!
train_inputs=np.matrix(X)
train_outputs=np.array(Y)


my_data_export = pd.DataFrame(np.concatenate((train_inputs, np.expand_dims(train_outputs, axis=1)), axis=1))
my_data_export.to_csv(r'export_data.csv')
        

rank_svm = RankSVM().fit(train_inputs, train_outputs)
    
