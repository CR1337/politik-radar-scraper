from typing import List
from string import ascii_lowercase, ascii_uppercase
from nltk.stem import SnowballStemmer


class Stemmer:

    _LANGUAGE: str = "german"
    _STEMMER: SnowballStemmer = SnowballStemmer(_LANGUAGE)

    @staticmethod
    def word_tokenize(text: str) -> List[str]:
        valid_characters = ascii_lowercase + ascii_uppercase + "- "
        text = "".join(c for c in text if c in valid_characters).lower()
        return text.split(" ")
    
    @classmethod
    def stem(cls, text: str) -> str:
        return " ".join(
            cls._STEMMER.stem(token).lower()
            for token in cls.word_tokenize(text)
        )
    