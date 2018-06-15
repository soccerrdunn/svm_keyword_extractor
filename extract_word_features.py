# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 22:20:36 2018

@author: Richard Dunn
"""
def extract_candidate_features(candidates, doc_text):
    import collections, math, nltk, re
    
    if type(candidates) is list:
        pass
    else:
        candidates=[candidates]
        
    candidate_scores = collections.OrderedDict()

    #get the text rank scores for the entire body to pull for each candidate later
    text_score = score_keyphrases_by_textrank(doc_text,.99,2)

    # get word counts for document
#    doc_word_counts = collections.Counter(word.lower()
#                                          for sent in nltk.sent_tokenize(doc_text)
#                                          for word in nltk.word_tokenize(sent))
    
    for candidate in candidates:
    
        #get the textrank score for the particular candidate, don't use this
        #if you're using key phrases and not just words, it will probably screwup
        textrank=0
        for keyword, score in text_score:
            if keyword == candidate:
                textrank = score


        
        pattern = re.compile(r'\b'+re.escape(candidate)+r'(\b|[,;.!?]|\s)', re.IGNORECASE)
        
        # frequency-based
        # number of times candidate appears in document
        cand_doc_count = len(pattern.findall(doc_text))
        # count could be 0 for multiple reasons; shit happens in a simplified example
        if not cand_doc_count:
            print ('**WARNING:', candidate, 'not found!')
            candidate_scores[candidate] = {'term_count': cand_doc_count,
                            'term_length': len(candidate),
                            'spread': 0,
                            'abs_first_occurrence': 0,
                            'abs_last_occurrence': 0,
                            'text_rank': textrank}
            continue

        # statistical
#        candidate_words = candidate.split()
#        max_word_length = max(len(w) for w in candidate_words)
#        term_length = len(candidate_words)
        term_length=len(candidate)
        # get frequencies for term and constituent words
        #sum_doc_word_counts = float(sum(doc_word_counts[w] for w in candidate_words))
 #       try:
            # lexical cohesion doesn't make sense for 1-word terms
 #           if term_length == 1:
 #               lexical_cohesion = 0.0
 #           else:
 #               lexical_cohesion = term_length * (1 + math.log(cand_doc_count, 10)) * cand_doc_count / sum_doc_word_counts
 #       except (ValueError, ZeroDivisionError) as e:
 #           lexical_cohesion = 0.0
        
        # positional
        # found in title, key excerpt
 #       in_title = 1 if pattern.search(doc_title) else 0
 #       in_excerpt = 1 if pattern.search(doc_excerpt) else 0
        # first/last position, difference between them (spread)
        doc_text_length = float(len(doc_text))
        first_match = pattern.search(doc_text)
        abs_first_occurrence = first_match.start() / doc_text_length
        if cand_doc_count == 1:
            spread = 0.0
            abs_last_occurrence = abs_first_occurrence
        else:
            for last_match in pattern.finditer(doc_text):
                pass
            abs_last_occurrence = last_match.start() / doc_text_length
            spread = abs_last_occurrence - abs_first_occurrence

        candidate_scores[candidate] = {'term_count': cand_doc_count,
                                       'term_length': term_length,
                                       'spread': spread,
                                       'abs_first_occurrence': abs_first_occurrence,
                                       'abs_last_occurrence': abs_last_occurrence,
                                       'text_rank': textrank}
#        candidate_scores_enumerated[candidate]=(cand_doc_count, term_length,
#                                                spread, abs_first_occurrence,
#                                                abs_last_occurrence,
#                                                textrank)
        

#        candidate_scores[candidate] = {'term_count': cand_doc_count,
#                                       'term_length': term_length, 'max_word_length': max_word_length,
#                                       'spread': spread, 'lexical_cohesion': lexical_cohesion,
#                                       'in_excerpt': in_excerpt, 'in_title': in_title,
#                                       'abs_first_occurrence': abs_first_occurrence,
#                                       'abs_last_occurrence': abs_last_occurrence}

    return candidate_scores