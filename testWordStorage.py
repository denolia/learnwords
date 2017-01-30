from multiprocessing import Process
import time
from words_storage import WordsStorage

storage = WordsStorage()

storage.add_word("utter", "вымолвить, произносить", "Аттер")


def check_loop():
    while(True):
        print(storage.check_hot_words())
        print(len(storage._storage))
        time.sleep(2)


if __name__ == '__main__':
    p = Process(target=check_loop)

    p.start()
    p.join()
