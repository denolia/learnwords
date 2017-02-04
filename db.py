from pprint import pprint

import psycopg2
from datetime import date

conn = psycopg2.connect(dbname='learnwords_db', user='learnwords', host='localhost', password='learnwords')
conn.autocommit = True

print(conn)
cur = conn.cursor()
cur.execute('SELECT version()')
ver = cur.fetchone()
print(ver)

# cur.execute("SELECT * FROM words")
# ver = cur.fetchall()
# pprint(ver)


def get_words_by_user(username):
    cur.execute("SELECT * FROM words")
    response = cur.fetchall()
    pprint(response)

def update_repeat_after(word_id, repeat_after, username):
    # TODO implement
    pass


def add_word_for_user(word, translation, pronunciation, date_unix, username):
    last_repeated = date.fromtimestamp(date_unix)
    # TODO calculate repeat_after
    repeat_after = date.fromtimestamp(date_unix)
    cur.execute("""INSERT INTO words VALUES (default, %s, %s, %s, %s, %s, %s)""",
                (word, translation, pronunciation,
                 last_repeated, repeat_after, username))


def get_words_to_repeat(date_unix, username):
    repeat_after = date.fromtimestamp(date_unix)
    cur.execute("SELECT id FROM words WHERE username=%s AND repeat_after<=%s",
                (username, repeat_after))
    return cur.fetchall()


def update_translation_of_word_for_user(word_id, translation,  username):
    # TODO what for?
    cur.execute("UPDATE words SET translation=%s WHERE id=%s AND username=%s", (translation, word_id, username))

    print("Number of rows updated: %d".format(cur.rowcount))


if __name__ == '__main__':
    get_words_by_user("julia_vikulina")

# for table in meta.tables:
#      print(table)
#
# slams = meta.tables['slams']
#
# clause = slams.insert().values(name='Wimbledon', country='United Kingdom')
#
# # con.execute(clause)
#
# clause = slams.insert().values(name='Roland Garros', country='France')
#
# # result = con.execute(clause)
# #
# # print(result)
# #
# # print(result.inserted_primary_key)
#
# victories = [
#     {'slam': 'Wimbledon', 'year': 2003, 'result': 'W'},
#     {'slam': 'Wimbledon', 'year': 2004, 'result': 'W'},
#     {'slam': 'Wimbledon', 'year': 2005, 'result': 'W'}
# ]
#
# # print(con.execute(meta.tables['results'].insert(), victories))
#
# results = meta.tables['results']
# print(results.c)
# for col in results.c:
#     print(col)
#
# clause = results.select().where(results.c.year == 2005)
# for row in con.execute(clause):
#     print(row)