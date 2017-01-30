import datetime


class WordsStorage:
    def __init__(self):
        self._storage = {}

    def add_word(self, word: str, translation: str, pronunciation: str,
                 repeat_after: datetime.timedelta = datetime.timedelta(seconds=10)):
        self._storage.update({word: {"translation": translation,
                                    "pronunciation": pronunciation,
                                    "last_repeated": datetime.datetime.now(), 
                                    "repeat_after": repeat_after}})

    def check_hot_words(self):
        hot_words = {}
        for word in self._storage.keys():
            date = self._storage.get(word).get("last_repeated")
            now = datetime.datetime.now()
            difference = self._storage.get(word).get("repeat_after")
            if now - date > difference:
                hot_words.update({word: self._storage.get(word)})
        return hot_words

    def show_all(self):
        return self._storage

