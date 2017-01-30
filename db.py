import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table


def connect(user, password, db, host='localhost', port=5432):
    """Returns a connection and a metadata object"""

    # We connect with the help of the PostgreSQL URL
    # postgresql://federer:grandestslam@localhost:5432/tennis
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con, reflect=True)

    return con, meta


con, meta = connect('federer', '123', 'tennis')
print(con)
print(meta)

# slams = Table('slams', meta,
#               Column('name', String, primary_key=True),
#               Column('country', String)
#               )
#
# results = Table('results', meta,
#                 Column('slam', String, ForeignKey('slams.name')),
#                 Column('year', Integer),
#                 Column('result', String)
#                 )
#
# # Create the above tables
# meta.create_all(con)

for table in meta.tables:
     print(table)

slams = meta.tables['slams']

clause = slams.insert().values(name='Wimbledon', country='United Kingdom')

# con.execute(clause)

clause = slams.insert().values(name='Roland Garros', country='France')

# result = con.execute(clause)
#
# print(result)
#
# print(result.inserted_primary_key)

victories = [
    {'slam': 'Wimbledon', 'year': 2003, 'result': 'W'},
    {'slam': 'Wimbledon', 'year': 2004, 'result': 'W'},
    {'slam': 'Wimbledon', 'year': 2005, 'result': 'W'}
]

# print(con.execute(meta.tables['results'].insert(), victories))

results = meta.tables['results']
print(results.c)
for col in results.c:
    print(col)

clause = results.select().where(results.c.year == 2005)
for row in con.execute(clause):
    print(row)