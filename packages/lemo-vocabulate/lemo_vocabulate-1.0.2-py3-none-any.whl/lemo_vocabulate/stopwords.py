"""
Stopword handling utilities
"""

from pathlib import Path
from typing import List, Set

class StopWordRemover:
    def __init__(self):
        self.stopwords: Set[str] = set()

    def build_stoplist(self, stoplist_text: str):
        self.stopwords = {word.strip().lower() for word in stoplist_text.split('\n') if word.strip()}

    def clear_stopwords(self, words: List[str]) -> List[str]:
        return [word for word in words if word not in self.stopwords]
    
    # ------------------- Load Stopwords -------------------
def load_stopwords_from_file(file_path: str, encoding: str = "utf-8") -> str:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Stopwords file not found: {file_path}.\nPlease provide a valid path to the stopwords file!")
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"Failed to decode {file_path} with encoding {encoding}: {e}")
