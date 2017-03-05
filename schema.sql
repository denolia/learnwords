DROP TABLE IF EXISTS words CASCADE;
CREATE TABLE words (
    id              BigSerial NOT NULL primary key,
    word            varchar(100),
    translation     varchar(100),
    pronunciation   varchar(80),
    last_repeated   timestamp,
    repeat_after    timestamp,
    delta           interval,
    username        varchar(80),
    state           smallint default 1
);
DROP TABLE IF EXISTS repetitions CASCADE;
CREATE TABLE repetitions (
    id              BigSerial NOT NULL primary key,
    word_id         int references words(id),
    username        varchar(80),
    date            timestamp,
    direction       int,
    status          int
);
