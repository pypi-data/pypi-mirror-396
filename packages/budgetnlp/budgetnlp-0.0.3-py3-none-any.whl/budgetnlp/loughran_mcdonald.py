import csv

from flashtext import KeywordProcessor
from .utils.download_data import _download_data
from .utils.text_normalization import _string_to_ascii, handle_data_tuples


url = "https://raw.githubusercontent.com/john-friedman/budgetnlp/main/data/loughran_mcdonald.csv"

NEGATIONS = {'not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing',
             'nowhere', 'cannot', "can't", "won't", "don't", "doesn't", 
             "didn't", "isn't", "aren't", "wasn't", "weren't", "without"}

# Lazy loading - initialized as None
_negative_processor = None
_complexity_processor = None
_uncertainty_processor = None


def _ensure_negative_processor():
    global _negative_processor
    
    if _negative_processor is None:
        file_path = _download_data(url, overwrite=False)
        negative_words = set()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['Negative']) > 0:
                    negative_words.add(row['Word'].lower())
        
        _negative_processor = KeywordProcessor(case_sensitive=False)
        for word in negative_words:
            _negative_processor.add_keyword(word)
    
    return _negative_processor


def _ensure_complexity_processors():
    global _complexity_processor, _uncertainty_processor
    
    if _complexity_processor is None:
        file_path = _download_data(url, overwrite=False)
        complexity_words = set()
        uncertainty_words = set()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['Complexity']) > 0:
                    complexity_words.add(row['Word'].lower())
                if int(row['Uncertainty']) > 0:
                    uncertainty_words.add(row['Word'].lower())
        
        _complexity_processor = KeywordProcessor(case_sensitive=False)
        for word in complexity_words:
            _complexity_processor.add_keyword(word)
        
        _uncertainty_processor = KeywordProcessor(case_sensitive=False)
        for word in uncertainty_words:
            _uncertainty_processor.add_keyword(word)
    
    return _complexity_processor, _uncertainty_processor


@handle_data_tuples
def negative_ratio(string, negation_reversals=True):
    processor = _ensure_negative_processor()
    
    string = _string_to_ascii(string)
    string_lower = string.lower()
    
    negative_matches = processor.extract_keywords(string_lower)
    negative_count = len(negative_matches)
    
    tokens = string_lower.split()
    total_words = len(tokens)
    
    if negation_reversals:
        reversals = 0
        for i in range(len(tokens) - 1):
            if tokens[i] in NEGATIONS and tokens[i + 1] in processor.extract_keywords(tokens[i + 1]):
                reversals += 1
        
        negative_count -= reversals
    
    return negative_count / max(total_words, 1)


@handle_data_tuples
def naive_complexity_ratio(string,complexity_weight=50, uncertainty_weight=30,sentence_weight=20,normal_sentence_length=20):

    complexity_proc, uncertainty_proc = _ensure_complexity_processors()
    
    string = _string_to_ascii(string)
    string_lower = string.lower()
    
    complexity_matches = complexity_proc.extract_keywords(string_lower)
    uncertainty_matches = uncertainty_proc.extract_keywords(string_lower)
    
    tokens = string_lower.split()
    total_words = len(tokens)
    
    complexity_ratio = len(complexity_matches) / max(total_words, 1)
    uncertainty_ratio = len(uncertainty_matches) / max(total_words, 1)
    
    # Calculate sentence lengths from input string
    sentences = [s.strip() for s in string.split('.') if s.strip()]
    sentence_lengths = [len(s.split()) for s in sentences]
    
    if len(sentence_lengths) > 0:
        mean_sentence_length = (sum(sentence_lengths)/len(sentence_lengths))/normal_sentence_length
    else:
        mean_sentence_length = 0
    
    score = (complexity_weight * complexity_ratio + uncertainty_weight * uncertainty_ratio + sentence_weight * mean_sentence_length)
    
    return score
