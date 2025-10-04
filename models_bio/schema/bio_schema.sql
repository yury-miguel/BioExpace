create table if not exists nasa.publication (
    id serial primary key,
    title varchar(255),
    url text,
    raw_html text,
    text_extratect text,
    dat_insercao timestamp default current_timestamp
);

create table if not exists nasa.llm_pipeline (
    id serial primary key,
    publication_id integer not null,
    stage varchar(50),
    status varchar(50) default 'pending',
    result_json jsonb,
    message text,
    dat_insercao timestamp default current_timestamp,
    constraint fk_publication foreign key (publication_id) references nasa.publications(id) on delete cascade
);


create table if not exists nasa.llm_memory (
    id serial primary key,
    pipeline_id integer not null,
    model_name varchar(50),
    chunk_index integer,
    context_json jsonb,
    dat_insercao timestamp default current_timestamp,
    constraint fk_pipeline foreign key (pipeline_id) references nasa.llm_pipeline(id) on delete cascade
);

create index if not exists idx_llm_pipeline_result_json on nasa.llm_pipeline using gin (result_json);
create index if not exists idx_llm_memory_context_json on nasa.llm_memory using gin (context_json);