from pprint import pprint

import psycopg2

conn = psycopg2.connect(dbname='learnwords_db', user='learnwords', host='localhost', password='learnwords')

print(conn)
cur = conn.cursor()
cur.execute('SELECT version()')
ver = cur.fetchone()
print(ver)

cur.execute("SELECT * FROM words")
ver = cur.fetchall()
pprint(ver)


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