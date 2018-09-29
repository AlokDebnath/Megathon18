drop table if exists students;
    create table students (
        id integer primary key autoincrement,
        name text not null,
        username text not null unique,
        password text not null,
        email text not null unique
    );

drop table if exists recruiters;
    create table recruiters (
        company text not null,
        email text not null unique,
        password text not null
    );