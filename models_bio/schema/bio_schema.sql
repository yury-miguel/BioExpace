create table if not exists nasa.publication (
    ii serial primary key,
    title varchar(255),
    url text,
    raw_html text,
    text_extratect text,
    dat_insercao timestamp default current_timestamp
);