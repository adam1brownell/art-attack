from flask import Flask, render_template, request, jsonify
import warnings
from nltk import (word_tokenize, pos_tag)
import requests
import re
from bs4 import BeautifulSoup
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

warnings.filterwarnings('ignore')
app = Flask(__name__)


def _get_soup_object(url, parser="html.parser"):
    return BeautifulSoup(requests.get(url).text, parser)


def get_online_def(term, disable_errors=False):
    if len(term.split()) > 1:
        print("Error: A Term must be only a single word")
    else:
        try:
            html = _get_soup_object("http://wordnetweb.princeton.edu/perl/webwn?s={0}".format(
                term))
            types = html.findAll("h3")
            lists = html.findAll("ul")
            out = {}
            for a in types:
                reg = str(lists[types.index(a)])
                meanings = []
                for x in re.findall(r'\((.*?)\)', reg):
                    if 'often followed by' in x:
                        pass
                    elif len(x) > 5 or ' ' in str(x):
                        meanings.append(x)
                name = a.text
                out[name] = meanings
            return out
        except Exception as e:
            if not disable_errors:
                return(term)
            else:
                return(e)


def clean_definition(definition):

    # only use the first clause of definition
    if ';' in definition:
        definition = re.split(';', definition)[0]

    # Get rid of indirect pronoun as the pronoun is most likely in the sentence already
    if (definition.split()[0] == 'a') or (definition.split()[0] == 'an'):
        definition = ' '.join(definition.split()[1:])

    # Get rid of the weird quirk where bad punctuation survives
    definition = re.sub('\(', '', definition)
    definition = re.sub('\`', '', definition)
    definition = re.sub('\'', '', definition)

    return definition


def define_a_word(word, correct_grammar):
    dictionary_entry = get_online_def(word)
    if dictionary_entry == word:
        return word
    acceptable_grammar_uses = list(dictionary_entry.keys())
    parts_of_speach = {'Noun': False, 'Verb': False, 'Pronoun': False, 'Adjective': False, 'Adverb': False}

    for grammar in parts_of_speach:
        if grammar in acceptable_grammar_uses:
            parts_of_speach[grammar] = True

    if not parts_of_speach[correct_grammar]:
        correct_grammar = list(dictionary_entry.keys())[0]

    best_definition = clean_definition(dictionary_entry[correct_grammar][0])

    return(best_definition)


def get_parts_of_speach_dictionary(sentence):
    pos_translator = {
        'CC': 'conjunction',
        'CD': 'digit',
        'DT': 'determiner',
        'EX': 'existential there',
        'FW': 'foreign word',
        'IN': 'preposition',
        'JJ': 'Adjective',
        'JJR': 'Adjective',
        'JJS': 'Adjective',
        'LS': 'list marker',
        'MD': 'modal',
        'NN': 'Noun',
        'NN': 'Noun',
        'NNS': 'Noun',
        'NNP': 'proper noun',
        'NNPS': 'proper noun',
        'PDT': 'predeterminer',
        'POS': 'possessive',
        'PRP': 'Pronoun',
        'PRP': 'Pronoun',
        'RB': 'Adverb',
        'RBR': 'Adverb',
        'RBS': 'Adverb',
        'RP': 'particle',
        'TO': 'to',
        'UH': 'Interjection',
        'VB': 'Verb',
        'VBD': 'Verb',
        'VBG': 'Verb',
        'VBN': 'Verb',
        'VBP': 'Verb',
        'VBZ': 'Verb',
        'WDT': 'determiner',
        'WP': 'Pronoun',
        'WP': 'Pronoun',
        'WRB': 'Abverb',
        'PRP$': 'Pronoun',
        ',': 'Punctuation',
        '.': 'Punctuation',
        }

    text = word_tokenize(sentence)
    tagged_words = pos_tag(text)
    clean_parts = {tagged_words[i][0]: pos_translator[tagged_words[i][1]] for i in range(len(tagged_words))}
    # Bug Fix: Inifintives 'to party' are marked as 'to' + 'noun' rather than 'to' + 'verb'
    infinitive_flag = False
    for key, val in clean_parts.items():
        if infinitive_flag:
            if clean_parts[key] == 'Noun':
                clean_parts[key] = 'Verb'
            infinitive_flag = False
        if val == 'to':
            infinitive_flag = True
    return(clean_parts)


def get_correct_grammar(word, pos_dictionary):
    # print(str(pos_dictionary))
    correct_pos = pos_dictionary[word]
    return(correct_pos)


def make_html_sentence(sentence_list):
    new_sentence_html = ["<span class='word'>" + word + " </span>" for word in sentence_list]
    return new_sentence_html


def more_define(word, sentence):
    pos_dictionary = get_parts_of_speach_dictionary(sentence)
    pos = get_correct_grammar(word, pos_dictionary)
    definition = define_a_word(word, pos)

    split_sent = sentence.split()
    index = split_sent.index(word)
    new_sentence_list = split_sent[:index] + definition.split() + split_sent[index+1:]
    new_sentence_html = make_html_sentence(new_sentence_list)
    return(''.join(new_sentence_html))


def clean_up(word, sentence):
    new_word = re.sub(r'\W+', '', word[:-1].lower())
    new_sentence = re.sub(word, new_word + ' ', sentence.lower())
    return new_word, new_sentence


@app.route("/")
def main():
    print('Root Call')
    return render_template('index.html')


@app.route("/define", methods=['POST'])
def test():
    clean_word, clean_sentence = clean_up(request.form.get('word'), request.form.get('sentence'))
    # print(clean_word)
    print(clean_sentence)
    new_sentence = more_define(word=clean_word, sentence=clean_sentence)
    data = {'new_sentence': new_sentence}
    data = jsonify(data)
    return data


if __name__ == "__main__":
    app.run(debug=True)
