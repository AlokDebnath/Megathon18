drop table if exists students;
    create table students (
        id integer primary key autoincrement,
        name text not null,
        username text not null unique,
        password text not null,
        github text,
        codeforces text,
        email text not null unique
    );

drop table if exists recruiters;
    create table recruiters (
        id integer primary key autoincrement,
        company text not null,
        email text not null unique,
        password text not null
    );

drop table if exists job_openings;
    create table job_openings (
        id integer primary key autoincrement,
        company_id integer not null,
        title text not null,
        FOREIGN KEY("company_id") REFERENCES recruiters("id") ON DELETE CASCADE
    );