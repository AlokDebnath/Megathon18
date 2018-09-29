drop table if exists students;
    create table students (
        id integer primary key autoincrement,
        name text not null,
        age integer not null,
        college text not null, 
        year integer not null,
        username text not null unique,
        password text not null,
        email text not null unique
    );

drop table if exists recruiters;
    create table recruiters (
        username text not null unique,
        company text not null,
        email text not null unique,
        password text not null
    );