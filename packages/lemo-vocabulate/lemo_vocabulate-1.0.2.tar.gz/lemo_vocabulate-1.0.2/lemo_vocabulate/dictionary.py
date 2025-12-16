"""
Dictionary loading and matching utilities
"""
import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

class CSVParser:
    @staticmethod
    def parse(file_path: str, delimiter: str = ',', quotechar: str = '"', encoding: str = 'utf-8') -> Tuple[List[str], List[List[str]]]:
        """Parse CSV file and return header and rows"""
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
            header = next(reader)
            rows = list(reader)
        return header, rows

class DictionaryData:
    def __init__(self):
        self.num_cats: int = 0
        self.max_words: int = 0
        self.cat_names: List[str] = []
        self.raw_word_counts: bool = True
        self.csv_delimiter: str = ","
        self.csv_quote: str = '"'
        self.output_captured_text: bool = False
        self.category_order: Dict[int, str] = {}
        self.concept_map: Dict[str, List[str]] = {}
        self.full_dictionary_map: Dict[str, Dict[int, Dict[str, str]]] = {'Wildcards': {}, 'Standards': {}}
        self.wildcard_arrays: Dict[int, List[str]] = {}
        self.precompiled_wildcards: Dict[str, re.Pattern] = {}
        self.dictionary_loaded: bool = False

# ------------------- Load Dictionary -------------------
class LoadDictionary:
    def load_dictionary_file(self, dict_data: DictionaryData, input_file: str,
                            encoding: str, csv_delimiter: str, csv_quote: str) -> DictionaryData:
        dict_data.max_words = 0
        dict_data.full_dictionary_map = {'Wildcards': {}, 'Standards': {}}
        dict_data.wildcard_arrays = {}
        dict_data.precompiled_wildcards = {}
        wildcard_lists: Dict[int, List[str]] = {}
        dict_data.concept_map = {}

        header, lines = CSVParser.parse(input_file, csv_delimiter, csv_quote, encoding)

        dict_data.num_cats = len(header) - 1
        dict_data.cat_names = header[1:]
        dict_data.category_order = {i: header[i+1] for i in range(dict_data.num_cats)}

        for line in lines:
            if not line or not line[0].strip():
                continue
            words_in_line = [w.strip() for w in line[0].split('|')]
            concept = words_in_line[0]
            categories_array = line[1:] if len(line) > 1 else []
            dict_data.concept_map[concept] = []

            for i, cat_value in enumerate(categories_array[:dict_data.num_cats]):
                if cat_value and cat_value.strip():
                    dict_data.concept_map[concept].append(dict_data.cat_names[i])

            for word_to_code in words_in_line:
                word_trimmed = word_to_code.strip().lower()
                if not word_trimmed:
                    continue
                words_in_entry = len(word_trimmed.split())
                dict_data.max_words = max(dict_data.max_words, words_in_entry)

                if '*' in word_trimmed:
                    if words_in_entry not in dict_data.full_dictionary_map['Wildcards']:
                        dict_data.full_dictionary_map['Wildcards'][words_in_entry] = {}
                        wildcard_lists[words_in_entry] = []
                    dict_data.full_dictionary_map['Wildcards'][words_in_entry][word_trimmed] = concept
                    wildcard_lists[words_in_entry].append(word_trimmed)
                    pattern = '^' + re.escape(word_trimmed).replace(r'\*', '.*')
                    dict_data.precompiled_wildcards[word_trimmed] = re.compile(pattern)
                else:
                    if words_in_entry not in dict_data.full_dictionary_map['Standards']:
                        dict_data.full_dictionary_map['Standards'][words_in_entry] = {}
                    dict_data.full_dictionary_map['Standards'][words_in_entry][word_trimmed] = concept

        for i in range(dict_data.max_words, 0, -1):
            if i in wildcard_lists:
                dict_data.wildcard_arrays[i] = wildcard_lists[i]

        dict_data.dictionary_loaded = True
        return dict_data

def match_dictionary(dict_data: DictionaryData, words: List[str]) -> Tuple[Dict[str, int], int, str, List[str]]:
    concept_counts = defaultdict(int)
    num_matched_tokens = 0
    captured = []
    nonmatched = []
    i = 0

    while i < len(words):
        matched = False
        for n in range(dict_data.max_words, 0, -1):
            if i + n > len(words):
                continue
            target = ' '.join(words[i:i+n])
            # Check standards
            if n in dict_data.full_dictionary_map['Standards'] and target in dict_data.full_dictionary_map['Standards'][n]:
                concept = dict_data.full_dictionary_map['Standards'][n][target]
                concept_counts[concept] += 1
                num_matched_tokens += n
                captured.append(target)
                i += n
                matched = True
                break
            # Check wildcards
            if n in dict_data.wildcard_arrays:
                for wildcard in dict_data.wildcard_arrays[n]:
                    if dict_data.precompiled_wildcards[wildcard].match(target):
                        concept = dict_data.full_dictionary_map['Wildcards'][n][wildcard]
                        concept_counts[concept] += 1
                        num_matched_tokens += n
                        captured.append(target)
                        i += n
                        matched = True
                        break
            if matched:
                break
        if not matched:
            nonmatched.append(words[i])
            i += 1

    captured_text = ' '.join(captured)
    return dict(concept_counts), num_matched_tokens, captured_text, nonmatched