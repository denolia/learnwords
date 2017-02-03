DROP TABLE IF EXISTS words CASCADE;
CREATE TABLE words (
    id              BigSerial NOT NULL primary key,
    word            varchar(100),
    translation     varchar(100),
    pronunciation   varchar(80),
    last_repeated   date,
    repeat_after    date,
    username        varchar(80)
);
DROP TABLE IF EXISTS repetitions CASCADE;
CREATE TABLE repetitions (
    id              BigSerial NOT NULL primary key,
    word_id         int references words(id),
    username        varchar(80),
    date            date,
    direction       int,
    status          int
);
