"""
Tokenization utilities for text processing
"""
import re
from typing import List

# ------------------- Tokenizer -------------------
class TwitterAwareTokenizer:
    """Tokenizer for social media text"""

    def __init__(self):
        self.urls = r"(?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.-]+[.](?:[a-z]{2,13})/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»""''])|(?:[a-z0-9]+(?:[.-][a-z0-9]+)*[.](?:[a-z]{2,13})\b/?(?!@))"
        self.emoticons = r"(?:[<>]?[:;=8][\-o\*\']?[\)\]\(\[dDpP/\:\}\{@\|\\]|[\)\]\(\[dDpP/\:\}\{@\|\\][\-o\*\']?[:;=8][<>]?|<3)"
        self.phonenumbers = r"(?:(?:\+?[01][*\-.\)]*)?(?:[\(]?\d{3}[*\-.\)]*)?\d{3}[*\-.\)]*\d{4})"
        self.htmltags = r"<[^>\s]+>"
        self.ascii_arrows = r"[\-]+>|<[\-]+"
        self.twitter_usernames = r"(?:@[\w_]+)"
        self.twitter_hashtag = r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"
        self.email = r"[\w.+-]+@[\w-]+\.(?:[\w-]\.?)+[\w-]"
        self.remaining_word_types = r"(?:[^\W\d_](?:[^\W\d_]|['\-_])+[^\W\d_])|(?:[+\-]?\d+[,/.:-]\d+[+\-]?)|(?:[\w_]+)|(?:\.(?:\s*\.){1,})|(?:\S)"

        all_patterns = [
            self.urls, self.phonenumbers, self.emoticons, self.htmltags,
            self.ascii_arrows, self.twitter_usernames, self.twitter_hashtag,
            self.email, self.remaining_word_types
        ]

        self.word_re = re.compile('|'.join(all_patterns), re.IGNORECASE)
        self.emoticon_re = re.compile(self.emoticons, re.IGNORECASE)
        self.hang_re = re.compile(r'([^a-zA-Z0-9])\1{3,}')
        self.reduce_lengthening_re = re.compile(r'(.)\1{2,}')

    def reduce_lengthening(self, text: str) -> str:
        return self.reduce_lengthening_re.sub(r'\1\1\1', text)

    def tokenize(self, text: str, reduce_len: bool = True, preserve_case: bool = False) -> List[str]:
        if reduce_len:
            text = self.reduce_lengthening(text)
        safe_text = self.hang_re.sub(r'\1\1\1', text)
        words = self.word_re.findall(safe_text)
        if not preserve_case:
            words = [w if self.emoticon_re.match(w) else w.lower() for w in words]
        return words

# ------------------- Whitespace Tokenizer -------------------
def tokenize_whitespace(text: str, method: str = 'new') -> list:
    """
    Tokenize text using either 'new' (URL/path-aware) or 'old' (simple split) method.
    """
    text = str(text).strip()
    if method.lower() == 'old':
        return text.split()
    elif method.lower() == 'new':
        import re
        initial_tokens = text.split()
        final_tokens = []
        for token in initial_tokens:
            if re.match(r'^https?://', token) or '.' in token:
                final_tokens.append(token)
            else:
                subtokens = [t for t in token.split('/') if t]
                final_tokens.extend(subtokens)
        return final_tokens
    else:
        raise ValueError("Invalid method. Choose 'old' or 'new'.")
