# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 16:43:28 2018

@author: Richard Dunn pulled from Burton DeWilde
"""
def extract_candidate_words(text, minlen = 3, good_tags=set(['JJ','JJR','JJS','NN','NNP','NNS','NNPS'])):
    import itertools, nltk, string, re

    # exclude candidates that are stop words or entirely punctuation
    punct = set(string.punctuation)
    stop_words = set(nltk.corpus.stopwords.words('english'))
    # tokenize and POS-tag words
    tagged_words = itertools.chain.from_iterable(nltk.pos_tag_sents(nltk.word_tokenize(sent)
                                                                    for sent in nltk.sent_tokenize(text)))
    # filter on certain POS tags and lowercase all words
    candidates = [word.lower() for word, tag in tagged_words
                  if tag in good_tags and word.lower() not in stop_words
                  and not all(char in punct for char in word)]
    clean_candidates=[]
    for candidate in candidates:
        if re.search(r'[a-zA-Z0-9_]*\-*[a-zA-Z0-9_]*', candidate).group() == '': continue #remove wonky candidates
        if len(candidate)>=minlen:
            clean_candidates.append(candidate)
            
    return clean_candidates

def score_keyphrases_by_textrank(text, n_keywords=0.01, minlen=3):
    from itertools import takewhile, tee
    import networkx, nltk
    
    # tokenize for all words, and extract *candidate* words
    words = [word.lower()
             for sent in nltk.sent_tokenize(text)
             for word in nltk.word_tokenize(sent)]
    candidates = extract_candidate_words(text, minlen)
    #remove some goofy punctuation, which causes issues
    #while '’' in candidates: 
    #   candidates.remove('’')
    # build graph, each node is a unique candidate

    graph = networkx.Graph()
    graph.add_nodes_from(set(candidates))
    # iterate over word-pairs, add unweighted edges into graph
    def pairwise(iterable):
        """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)
    for w1, w2 in pairwise(candidates):
        if w2:
            graph.add_edge(*sorted([w1, w2]))
    # score nodes using default pagerank algorithm, sort by score, keep top n_keywords
    ranks = networkx.pagerank(graph)
    if 0 < n_keywords < 1:
        n_keywords = int(round(len(candidates) * n_keywords))
    word_ranks = {word_rank[0]: word_rank[1]
                  for word_rank in sorted(iter(ranks.items()), key=lambda x: x[1], reverse=True)[:n_keywords]}
    keywords = set(word_ranks.keys())
    # merge keywords into keyphrases
    keyphrases = {}
    j = 0
    for i, word in enumerate(words):
        if i < j:
            continue
        if word in keywords:
            kp_words = word
            #kp_words = list(takewhile(lambda x: x in keywords, words[i:i+10]))
            avg_pagerank=(word_ranks[word])
            #avg_pagerank = sum(word_ranks[w] for w in kp_words) / float(len(kp_words))
            keyphrases[word]=avg_pagerank
            #keyphrases[' '.join(kp_words)] = avg_pagerank
            # counter as hackish way to ensure merged keyphrases are non-overlapping
            j = i + len(kp_words)
    
    return sorted(iter(keyphrases.items()), key=lambda x: x[1], reverse=True)

