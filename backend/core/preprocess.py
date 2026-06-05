import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
import os

# cek dan download data NLTK yang dibutuhkan
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        nltk.download('stopwords', quiet=True)
    except Exception:
        pass

stemmer = PorterStemmer()
try:
    stop_words_set = set(stopwords.words('english'))
except Exception:
    # fallback jika download NLTK gagal
    stop_words_set = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
                      "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
                      "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
                      "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
                      "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
                      "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
                      "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
                      "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
                      "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
                      "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
                      "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
                      "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"}

def preprocess_text(text: str, apply_stemming: bool = True, remove_stopwords: bool = True):
    import re
    text = text.lower()

    try:
        tokens = word_tokenize(text)
    except Exception:
        # fallback jika punkt tidak tersedia
        tokens = re.findall(r'\b\w+\b', text)

    # buang tanda baca
    tokens = [t for t in tokens if t not in string.punctuation]

    if remove_stopwords:
        tokens = [t for t in tokens if t not in stop_words_set]

    if apply_stemming:
        tokens = [stemmer.stem(t) for t in tokens]

    return tokens
