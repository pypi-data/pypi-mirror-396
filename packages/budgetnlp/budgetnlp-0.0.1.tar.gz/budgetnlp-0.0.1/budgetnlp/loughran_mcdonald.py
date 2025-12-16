import csv

from flashtext import KeywordProcessor
from .utils.download_data import _download_data
from .utils.text_normalization import _string_to_ascii, handle_data_tuples


url = "https://raw.githubusercontent.com/john-friedman/budgetnlp/main/data/loughran_mcdonald.csv"
file_path = _download_data(url, overwrite=False)

NEGATIONS = {'not', 'no', 'never', 'none', 'neither', 'nobody', 'nothing',
             'nowhere', 'cannot', "can't", "won't", "don't", "doesn't", 
             "didn't", "isn't", "aren't", "wasn't", "weren't", "without"}

NEGATIVE_WORDS = set()

with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if int(row['Negative']) > 0:
            NEGATIVE_WORDS.add(row['Word'].lower())

processor = KeywordProcessor(case_sensitive=False)
for word in NEGATIVE_WORDS:
    processor.add_keyword(word)





@handle_data_tuples
def negative_ratio(string, negation_reversals=True):
    string = _string_to_ascii(string)
    string_lower = string.lower()
    
    negative_matches = processor.extract_keywords(string_lower)
    negative_count = len(negative_matches)
    
    tokens = string_lower.split()
    total_words = len(tokens)
    
    if negation_reversals:
        reversals = 0
        for i in range(len(tokens) - 1):
            if tokens[i] in NEGATIONS and tokens[i + 1] in NEGATIVE_WORDS:
                reversals += 1
        
        negative_count -= reversals
    
    return negative_count / max(total_words,1)

