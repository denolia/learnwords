import logging
from datetime import datetime, timedelta
from pprint import pprint

import psycopg2

from enums import Mode

log = logging.getLogger(__name__)


conn = psycopg2.connect(dbname='learnwords_db', user='learnwords', host='192.168.1.64', password='learnwords')
conn.autocommit = True

log.info("Connection with database established: {}".format(conn))
cur = conn.cursor()
cur.execute('SELECT version()')
ver = cur.fetchone()
log.info("Using version: {}".format(ver))

# TODO move this to settings
fetch_koeff = dict(fetched=2, not_fetched=1)


def get_words_by_user(username):
    cur.execute("SELECT * FROM words WHERE username=%s", (username,))
    response = cur.fetchall()
    pprint(response)


def add_word_for_user(word, translation, pronunciation, last_repeated, delta, username):
    last_repeated_datetime = datetime.fromtimestamp(last_repeated)
    interval = timedelta(days=delta)
    repeat_after = last_repeated_datetime + interval
    # TODO here to set state depending on what is translation
    cur.execute("""INSERT INTO words VALUES (default, %s, %s, %s, %s, %s, %s, %s, default)""",
                (word, translation, pronunciation,
                 last_repeated_datetime,
                 repeat_after, interval, username))


def count_words(username):
    cur.execute("SELECT count(*) FROM words WHERE username=%s",
                (username,))
    return cur.fetchone()[0]


def count_words_to_mode(username: str, mode: Mode):
    if mode == Mode.learn:
        cur.execute("SELECT count(*) FROM words WHERE username=%s AND state=1",
                    (username,))
    else:
        repeat_after = datetime.now()
        cur.execute("SELECT count(*) FROM words WHERE username=%s AND state=2 AND repeat_after<=%s",
                    (username, repeat_after))
    return cur.fetchone()[0]


def count_words_green(username):
    cur.execute("SELECT count(*) FROM words WHERE username=%s AND state=2",
                (username,))
    num_repeat_state = cur.fetchone()[0]
    num_ready_to_repeat = count_words_to_mode(username, Mode.repeat)
    return num_repeat_state - num_ready_to_repeat


def get_one_word_to_learn(username):
    cur.execute("SELECT * FROM words WHERE username=%s AND state=1 LIMIT 1",
                (username,))
    return cur.fetchone()


def get_one_word_to_repeat(date_unix, username):
    repeat_after = datetime.fromtimestamp(date_unix)
    cur.execute("SELECT id, word FROM words WHERE username=%s "
                "AND state=2 AND repeat_after<=%s "
                "ORDER BY repeat_after DESC LIMIT 1",
                (username, repeat_after))
    return cur.fetchone()


def get_word_by_id(word_id, username):
    cur.execute("SELECT * FROM words WHERE id=%s AND username<=%s LIMIT 1",
                (word_id, username))
    return cur.fetchone()


def set_repeated_word(word_id, date_unix, direction, status, username):
    last_repeated = datetime.fromtimestamp(date_unix)

    word = get_word_by_id(word_id, username)
    delta = timedelta(0)
    if status == 0:
        delta = word[6] * fetch_koeff['fetched']
    elif status == -1:
        delta = word[6] * fetch_koeff['not_fetched']

    if delta == timedelta(0):
        delta = timedelta(days=1)

    repeat_after = last_repeated + delta
    cur.execute("UPDATE words SET last_repeated=%s, repeat_after=%s, delta=%s WHERE id=%s AND username=%s",
                (last_repeated, repeat_after, delta, word_id, username))
    cur.execute("""INSERT INTO repetitions VALUES (default, %s, %s, %s, %s, %s)""",
                (word_id, username, last_repeated, direction, status))
    log.debug("Number of rows updated: {}".format(cur.rowcount))
    return repeat_after


def set_learnt_word(word_id, date_unix, status, username):
    last_repeated = datetime.fromtimestamp(date_unix)

    delta = timedelta(days=1)

    if status == 2:
        repeat_after = last_repeated + delta
    else:
        repeat_after = last_repeated
        delta = timedelta(0)

    cur.execute("UPDATE words SET state=%s, last_repeated=%s, repeat_after=%s, delta=%s WHERE id=%s AND username=%s",
                (status, last_repeated, repeat_after, delta, word_id, username))
    log.debug("Number of rows updated: {}".format(cur.rowcount))
    return repeat_after


def update_translation_of_word_for_user(word_id, translation, username):
    # TODO what for?
    cur.execute("UPDATE words SET translation=%s WHERE id=%s AND username=%s", (translation, word_id, username))

    log.debug("Number of rows updated: {}".format(cur.rowcount))


if __name__ == '__main__':
    get_words_by_user("julia_vikulina")
