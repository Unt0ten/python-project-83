CREATE TABLE urls (
    id         bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name       varchar(255) UNIQUE NOT NULL,
    created_at date DEFAULT CURRENT_DATE
);

CREATE TABLE url_checks(
    id           bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id       bigint REFERENCES urls (id),
    status_code  bigint,
    h1           varchar(255),
    title        varchar(255),
    description  text,
    created_at   date DEFAULT CURRENT_DATE
);