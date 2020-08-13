import spacy
import pandas
from collections import Counter
from spacy.matcher import Matcher
import pickle
import csv

""" This code extracts all the adj-adj-n and adj-adj-adj-n sets from a set
    of 13,848 movie synopses from:
    https://www.kaggle.com/cryptexcode/mpst-movie-plot-synopses-with-tags

    Then it takes those groupings and calculates the Nominal Character
    score for each of the adjectives in order to see if more noun-like
    adjectives appear closer to the noun as claimed in Biber et al(1999).
"""
article_data = '/Users/amaris/Desktop/mpst_full_data.csv'
nlp = spacy.load("en")

# Find all the adj-adj-n and adj-adj-adj-n sets in the data set, and create
# data structures to store the info for use later
# Matching code adapted from Spacy documentation on rule based matching.
# https://spacy.io/usage/rule-based-matching

aan_matcher = Matcher(nlp.vocab)
pattern = [{"POS": "ADJ"}, {"POS": "ADJ"}, {"POS": "NOUN"}]
aan_matcher.add("AAN", None, pattern)

aaan_matcher = Matcher(nlp.vocab)
pattern = [{"POS": "ADJ"}, {"POS": "ADJ"}, {"POS": "ADJ"}, {"POS": "NOUN"}]
aaan_matcher.add("AAAN", None, pattern)

article_dataframe = pandas.read_csv(article_data, error_bad_lines=False,
                                    encoding='utf-8')
aan_list = []
aaan_list = []

adj_counts = Counter()
noun_counts = Counter()

for row in article_dataframe['plot_synopsis']:
    doc = nlp(row)

    for token in doc:
        if token.pos_ == 'ADJ':
            adj_counts[token.text] += 1
        elif token.pos_ == 'NOUN':
            noun_counts[token.text] += 1

    aan_matches = aan_matcher(doc)
    aaan_matches = aaan_matcher(doc)

    for match_id, start, end in aan_matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        aan_list.append(span.text)
        # print(match_id, string_id, start, end, span.text)

    for match_id, start, end in aaan_matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        aaan_list.append(span.text)
        # print(match_id, string_id, start, end, span.text)


adj_and_nouns = []
for key in adj_counts:
    if key in noun_counts:
        adj_and_nouns.append(key)

# Option: Pickle data so it doesn't have to be parsed and processed
# every time the program runs.
with open('adj.pickle', 'wb') as adj_file:
    pickle.dump(adj_counts, adj_file, protocol=pickle.HIGHEST_PROTOCOL)
with open('noun.pickle', 'wb') as n_file:
    pickle.dump(noun_counts, n_file, protocol=pickle.HIGHEST_PROTOCOL)
with open('aan.pickle', 'wb') as aan_file:
    pickle.dump(aan_list, aan_file, protocol=pickle.HIGHEST_PROTOCOL)
with open('aaan.pickle', 'wb') as aaan_file:
    pickle.dump(aaan_list, aaan_file, protocol=pickle.HIGHEST_PROTOCOL)
with open('adj_and_nouns.pickle', 'wb') as item_file:
    pickle.dump(adj_and_nouns, item_file, protocol=pickle.HIGHEST_PROTOCOL)

# Unpickle data if using above pickle files to evaluate data.
with open('adj.pickle', 'rb') as adj_data:
    adj = pickle.load(adj_data)
with open('noun.pickle', 'rb') as n_data:
    noun = pickle.load(n_data)
with open('aan.pickle', 'rb') as aan_data:
    aan = pickle.load(aan_data)
with open('adj_and_nouns.pickle', 'rb') as adj_n_data:
    adj_and_nouns = pickle.load(adj_n_data)
with open('aaan.pickle', 'rb') as aaan_data:
    aaan = pickle.load(aaan_data)


def nomchar(word):
    """ Calculate the Nominal Character score of a word. To calculate
        the score, find the number of times a word is tagged as an adj
        and divide it by the sum of the times that word is tagged as a
        noun with the times it is tagged as an adj. Then subtract that
        number from 1. Higher values mean the word is more noun-like.
    """
    if word in adj_and_nouns:
        n = noun[word]
        a = adj[word]
    elif word in adj and word not in noun:
        n = 0
        a = adj[word]
    elif word in noun and word not in adj:
        n = noun[word]
        a = 0
    else:
        n = 0
        a = 0
    score = 1-(a/(a + n))
    return score


with open('aan_results.csv', 'w') as aan_res:
    writer = csv.writer(aan_res, delimiter='\t', lineterminator='\n')
    a1_count = 0
    a2_count = 0
    equal_count = 0

    for row in aan:
        if len(row.split()) == 3:
            adj1, adj2, nn = row.split()
            index_1 = nomchar(adj1)
            index_2 = nomchar(adj2)
            # print("Index 1: {} \nIndex 2: {}\n".format(index_1, index_2))
            if index_1 > index_2:
                a1_count += 1
                # print("Adjective 1 is more nouny")
            elif index_2 > index_1:
                a2_count += 1
                # print("Adjective 2 is more nouny")
            else:
                equal_count += 1
                # print("Equal scores")
            writer.writerow((row, index_1, index_2))

print("Adjective One: {}\nAdjective Two: {}\nEqual: {}"
      .format(a1_count, a2_count, equal_count))

with open('aaan_results.csv', 'w') as aaan_res:
    writer = csv.writer(aaan_res, delimiter='\t', lineterminator='\n')
    a1_count = 0
    a2_count = 0
    a3_count = 0
    equal_count = 0

    for row in aaan:
        if len(row.split()) == 4:
            adj1, adj2, adj3, nn = row.split()
            index_1 = nomchar(adj1)
            index_2 = nomchar(adj2)
            index_3 = nomchar(adj3)
            # print("Index 1: {} \nIndex 2: {}\n".format(index_1, index_2))
            if index_1 > index_2 and index_1 > index_3:
                a1_count += 1
                # print("Adjective 1 is more nouny")

            elif index_2 > index_1 and index_2 > index_3:
                a2_count += 1
                # print("Adjective 2 is more nouny")

            elif index_3 > index_2 and index_3 > index_1:
                a3_count += 1
                # print("Adjective 2 is more nouny")
            else:
                equal_count += 1
                # print("Equal scores")

            writer.writerow((row, index_1, index_2, index_3))

print("Adjective One: {}\nAdjective Two: {}\nAdjective Three: {}\nEqual: {}"
      .format(a1_count, a2_count, a3_count, equal_count))
