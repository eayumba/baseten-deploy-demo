from collections import Counter
import string
import re
import enums

class Preprocess:
    def __init__(self, text: str):
        self.text = text
        self.text = self.remove_punctuation()
        self.text = self.remove_stopwords()
        self.text = self.remove_freqwords()
        self.text = self.remove_urls()

    def remove_punctuation(self):
        PUNCT_TO_REMOVE = string.punctuation

        return self.text.translate(str.maketrans(" ", " ", PUNCT_TO_REMOVE))

    def remove_stopwords(self):
        
        self.text = [
            word
            for word in self.text.split()
            if word not in enums.STOPWORDS and len(word) > 2
        ]
        return " ".join(self.text)

    def remove_freqwords(self):

        cnt = Counter()
        for t in self.text:
            for word in t.split():
                cnt[word] += 1
        FREQWORDS = set([w for (w, wc) in cnt.most_common(10)])

        """custom function to remove the frequent words"""
        return " ".join(
            [word for word in str(self.text).split() if word not in FREQWORDS]
        )

    def remove_urls(self):
        url_pattern = re.compile(r"https?://\S+|www\.\S+")
        return url_pattern.sub(r"", self.text)
