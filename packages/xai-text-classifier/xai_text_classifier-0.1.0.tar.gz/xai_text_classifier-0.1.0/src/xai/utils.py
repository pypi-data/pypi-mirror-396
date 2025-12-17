import re
import pandas as pd
import numpy as np
import string
from collections import Counter
from textblob import TextBlob
import textstat
import spacy
from scipy.stats import entropy
import shap
import gzip
from nltk.corpus import stopwords
import shap
import xgboost as xgb
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import re
import language_tool_python
from collections import Counter
import math
from textblob import Word
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_sm")

tool = language_tool_python.LanguageTool('en-US')

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words('english'))

FEATURES = [ 'character_count',
       'word_count', 'sentence_count', 'paragraph_count', 'stopword_count',
       'unique_word_count', 'sentiment_polarity',
       'sentiment_subjectivity', 'discourse_marker_count', 'vocab_size',
       'sentence_complexity', 'punctuation_count',
       'sentence_length_difference', 'type_token_ratio', 'word_entropy',
       'flesch_reading_ease', 'gzip_ratio', 'negation_freq',
       'question_stmt_ratio', 'clause_sentence_ratio', 'modal_freq',
       'pronoun_ratio', 'pos_diversity', 'hapax_ratio',
       'sentence_length_variation', 'repetition_rate', 'personal_voice_score',
       'emotion_variation', 'specificity_score', 'figurative_language_score',
       'paragraph_coherence_consistency', 'predictability_score',
       'hedge_uncertainty_score', 'transition_variety_score',
       'grammatical_mistakes', 'pos_2gram_variety', 'pos_3gram_variety',
       'pos_4gram_variety'
]
TARGET = 'label'
# Define all feature functions
def vocabSize(sentence):
    doc = nlp(sentence.lower())
    tokens = set([token.text for token in doc if not token.is_punct])
    return len(tokens)

def sentence_complexity(sentence):
    flesch_score = textstat.flesch_reading_ease(sentence)
    fk_grade_level = textstat.flesch_kincaid_grade(sentence)
    gunning_fog = textstat.gunning_fog(sentence)
    smog_index = textstat.smog_index(sentence)
    composite_score = (flesch_score * 0.2 + fk_grade_level * 0.3 + 
                      gunning_fog * 0.3 + smog_index * 0.2)
    return composite_score

def punctuation_count(paragraph):
    return sum(1 for char in paragraph if char in string.punctuation)

def sentence_length_difference(paragraph):
    sentences = re.split(r'[.!?]', paragraph)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 0
    sentence_lengths = [len(s.split()) for s in sentences]
    return max(sentence_lengths) - min(sentence_lengths)

def type_token_ratio(text):
    words = text.split()
    if len(words) == 0:
        return 0
    unique_words = set(words)
    return len(unique_words) / len(words)

def pos_counts(text):
    doc = nlp(text)
    pos_count_dict = {}
    for token in doc:
        pos = token.pos_
        pos_count_dict[pos] = pos_count_dict.get(pos, 0) + 1
    return pos_count_dict

def count_discourse_markers(text):
    discourse_markers = ["however", "therefore", "although", "nevertheless", "hence"]
    return sum(text.lower().count(marker) for marker in discourse_markers)

def word_entropy(text):
    doc = nlp(text)
    words = [t.lemma_.lower() for t in doc if t.is_alpha]
    if not words:
        return 0
    freqs = list(Counter(words).values())
    return entropy(freqs)

def flesch_reading_ease(text):
    try:
        return textstat.flesch_reading_ease(text)
    except:
        return 0

def gzip_ratio(text):
    if len(text) == 0:
        return 0
    compressed = len(gzip.compress(text.encode('utf-8')))
    return compressed / len(text)

def negation_frequency(text):
    doc = nlp(text)
    negations = [t for t in doc if t.dep_ == "neg" or 
                 t.lemma_.lower() in ["not", "no", "never", "none", "n't"]]
    total_words = len([t for t in doc if t.is_alpha])
    return len(negations) / (total_words + 1e-5)

def question_statement_ratio(text):
    doc = nlp(text)
    sentences = list(doc.sents)
    if not sentences:
        return 0
    question_count = sum(1 for s in sentences if s.text.strip().endswith("?"))
    statement_count = sum(1 for s in sentences if s.text.strip().endswith("."))
    return question_count / (statement_count + 1e-5)

def clause_to_sentence_ratio(text):
    doc = nlp(text)
    sentences = list(doc.sents)
    if not sentences:
        return 0
    clause_markers = ("mark", "advcl", "ccomp", "xcomp", "acl", "relcl", "conj")
    clause_count = sum(1 for t in doc if t.dep_ in clause_markers)
    return clause_count / len(sentences)

def modal_verb_frequency(text):
    doc = nlp(text)
    modals = {"can", "could", "may", "might", "shall", "should", "will", "would", "must"}
    modal_count = sum(1 for t in doc if t.lemma_.lower() in modals)
    total_words = len([t for t in doc if t.is_alpha])
    return modal_count / (total_words + 1e-5)

def pronoun_ratio(text):
    doc = nlp(text)
    pronouns = [t for t in doc if t.pos_ == "PRON"]
    total_words = len([t for t in doc if t.is_alpha])
    return len(pronouns) / (total_words + 1e-5)

def pos_diversity(text):
    doc = nlp(text)
    pos_tags = [t.pos_ for t in doc if t.is_alpha]
    if not pos_tags:
        return 0
    counts = Counter(pos_tags)
    return entropy(list(counts.values()))

def hapax_legomena_ratio(text):
    doc = nlp(text)
    words = [t.lemma_.lower() for t in doc if t.is_alpha]
    if not words:
        return 0
    freqs = Counter(words)
    hapax = sum(1 for w, f in freqs.items() if f == 1)
    return hapax / len(freqs)

def get_sentiment_polarity(text):
    return TextBlob(text).sentiment.polarity

def get_sentiment_subjectivity(text):
    return TextBlob(text).sentiment.subjectivity

def count_stopwords(text):
    return len([word for word in text.split() if word.lower() in stop_words])

def grammatical_mistakes(sentence):

  mistakes = len(tool.check(sentence))

  return mistakes

def pos_tag_ngrams(text, n=2):
    doc = nlp(text)
    tags = [token.pos_ for token in doc if token.is_alpha]

    if len(tags) < n:
        return {}

    ngrams = zip(*[tags[i:] for i in range(n)])
    return Counter(ngrams)

def pos_ngram_variety(text, n=2):
    ngrams = pos_tag_ngrams(text, n)
    return len(ngrams)

def sentence_length_variation(text):
    sentences = sent_tokenize(text)
    lengths = [len(s.split()) for s in sentences if len(s.split()) > 0]

    if len(lengths) < 2:
        return 0.0  

    return np.std(lengths)   # Standard deviation

def repetition_rate(text):
    words = [w.lower() for w in text.split()]
    bigrams = [(words[i], words[i+1]) for i in range(len(words)-1)]
    if len(bigrams) == 0:
        return 0

    counts = Counter(bigrams)
    repeated = sum(1 for bg, c in counts.items() if c > 1)

    return repeated / len(bigrams)

def personal_voice_score(text):
    personal_pronouns = {"i", "me", "my", "mine", "we", "us", "our", "ours"}
    words = [w.lower() for w in text.split()]
    count = sum(1 for w in words if w in personal_pronouns)
    if len(words) == 0:
        return 0
    return count / len(words)

def emotion_variation(text):
    sentences = sent_tokenize(text)
    if len(sentences) < 2:
        return 0

    sentiments = [TextBlob(s).sentiment.polarity for s in sentences]
    diffs = [abs(sentiments[i] - sentiments[i+1]) for i in range(len(sentiments)-1)]

    return np.mean(diffs)


def specificity_score(text):
    doc = nlp(text)
    concrete_tags = {"NOUN", "PROPN", "NUM"}  
    concrete_count = sum(1 for token in doc if token.pos_ in concrete_tags)
    if len(doc) == 0:
        return 0
    return concrete_count / len(doc)


def imperfection_score(text):
    words = [w for w in re.findall(r"\b\w+\b", text)]
    if len(words) == 0:
        return 0

    misspelled = sum(1 for w in words if Word(w).correct().lower() != w.lower())
    return misspelled / len(words)

figurative_markers = [
    "like", "as if", "as though", "metaphor", "symbolic", 
    "resembles", "reminds me of", "figurative"
]

def figurative_language_score(text):
    t = text.lower()
    count = sum(t.count(m) for m in figurative_markers)
    return count

def paragraph_coherence_consistency(text):
    paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 0]

    if len(paragraphs) < 2:
        return 0

    vec = TfidfVectorizer().fit_transform(paragraphs)
    sims = []

    for i in range(len(paragraphs)-1):
        sim = cosine_similarity(vec[i], vec[i+1])[0][0]
        sims.append(sim)

    return np.mean(sims)


def predictability_score(text):
    words = [w.lower() for w in text.split()]
    counts = Counter(words)
    total = len(words)
    if total == 0:
        return 0

    probs = [counts[w]/total for w in words]
    surprise = [-math.log(p) for p in probs]

    return np.mean(surprise)

hedge_words = {
    "maybe", "perhaps", "sort of", "kind of", "i guess", 
    "probably", "possibly", "apparently", "roughly"
}

def hedge_uncertainty_score(text):
    t = text.lower()
    count = sum(t.count(hw) for hw in hedge_words)
    return count

transitions = [
    "however", "therefore", "meanwhile", "moreover", "furthermore",
    "in contrast", "on the other hand", "overall", "in summary"
]

def transition_variety_score(text):
    t = text.lower()
    count = sum(t.count(word) for word in transitions)
    return count

def get_features_from_text(text: str):
    stop_words = set(stopwords.words('english'))

    data = {
        'character_count': len(text),
        'word_count': len(text.split()),
        'sentence_count': len(sent_tokenize(text)),
        'paragraph_count': len(text.split("\n")),
        'stopword_count': len([w for w in text.split() if w.lower() in stop_words]),
        'unique_word_count': len(set(text.split())),
        'sentiment_polarity': TextBlob(text).sentiment.polarity,
        'sentiment_subjectivity': TextBlob(text).sentiment.subjectivity,
        'discourse_marker_count': count_discourse_markers(text),
        'vocab_size': vocabSize(text),
        'sentence_complexity': sentence_complexity(text),
        'punctuation_count': punctuation_count(text),
        'sentence_length_difference': sentence_length_difference(text),
        'type_token_ratio': type_token_ratio(text),
        'word_entropy': word_entropy(text),
        'flesch_reading_ease': flesch_reading_ease(text),
        'gzip_ratio': gzip_ratio(text),
        'negation_freq': negation_frequency(text),
        'question_stmt_ratio': question_statement_ratio(text),
        'clause_sentence_ratio': clause_to_sentence_ratio(text),
        'modal_freq': modal_verb_frequency(text),
        'pronoun_ratio': pronoun_ratio(text),
        'pos_diversity': pos_diversity(text),
        'hapax_ratio': hapax_legomena_ratio(text),
        'sentence_length_variation' : sentence_length_variation(text),
        'repetition_rate' : repetition_rate(text),
        'personal_voice_score' : personal_voice_score(text),
        'emotion_variation' : emotion_variation(text),
        'specificity_score' : specificity_score(text),
        'figurative_language_score' : figurative_language_score(text),
        'paragraph_coherence_consistency' : paragraph_coherence_consistency(text),
        'predictability_score' : predictability_score(text),
        'hedge_uncertainty_score' : hedge_uncertainty_score(text),
        'transition_variety_score' : transition_variety_score(text),
        'grammatical_mistakes':grammatical_mistakes(text),
        'pos_2gram_variety':pos_ngram_variety(text),
        'pos_3gram_variety':pos_ngram_variety(text,n=3),
        'pos_4gram_variety':pos_ngram_variety(text,n=4)
    }
    
    return pd.DataFrame([data])[FEATURES]