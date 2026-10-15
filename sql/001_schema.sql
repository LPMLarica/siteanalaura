-- =====================================================================
-- Agenda Psicóloga Ana Laura — schema do banco (Supabase / PostgreSQL)
--
-- Idempotente: pode ser executado mais de uma vez sem apagar dados.
-- Execute no Supabase em SQL Editor → New query → Run.
--
-- Segurança: o app acessa o banco DIRETAMENTE (connection string), não
-- pela API REST do Supabase. Por isso o RLS fica LIGADO e SEM políticas
-- em todas as tabelas, e os papéis públicos (anon/authenticated) não têm
-- permissão nenhuma: a chave pública do projeto não dá acesso a dados.
-- =====================================================================

create table if not exists public.users (
    id                      serial primary key,
    supabase_uid            varchar(64)  not null unique,
    name                    varchar(200) not null,
    email                   varchar(200) not null unique,
    professional_register   varchar(50),
    phone                   varchar(30),
    default_session_minutes integer      not null default 50,
    default_session_value   numeric(10, 2),
    active                  boolean      not null default true,
    created_at              timestamptz  not null default now(),
    updated_at              timestamptz  not null default now()
);

create table if not exists public.patients (
    id                serial primary key,
    user_id           integer      not null references public.users (id) on delete cascade,
    full_name         varchar(150) not null,
    cpf               varchar(14),
    birth_date        date,
    phone             varchar(30),
    email             varchar(150),
    address           varchar(255),
    emergency_contact varchar(200),
    notes             text,
    status            varchar(30)  not null default 'Ativo',
    session_value     numeric(10, 2),
    created_at        timestamptz  not null default now(),
    updated_at        timestamptz  not null default now()
);
create index if not exists ix_patients_user_name on public.patients (user_id, full_name);

create table if not exists public.consultations (
    id          serial primary key,
    user_id     integer      not null references public.users (id) on delete cascade,
    patient_id  integer      not null references public.patients (id) on delete cascade,
    date        date         not null,
    start_time  time         not null,
    end_time    time         not null,
    title       varchar(255) not null default 'Sessão',
    status      varchar(30)  not null default 'Agendada',
    modality    varchar(30)  not null default 'Presencial',
    observation text,
    created_at  timestamptz  not null default now(),
    updated_at  timestamptz  not null default now(),
    constraint ck_consultations_time check (end_time > start_time)
);
create index if not exists ix_consultations_user_date  on public.consultations (user_id, date);
create index if not exists ix_consultations_patient_id on public.consultations (patient_id);

create table if not exists public.payments (
    id              serial primary key,
    user_id         integer        not null references public.users (id) on delete cascade,
    patient_id      integer        not null references public.patients (id) on delete cascade,
    consultation_id integer        not null references public.consultations (id) on delete cascade,
    amount          numeric(10, 2) not null default 0,
    payment_method  varchar(50),
    payment_date    date,
    status          varchar(30)    not null default 'Pendente',
    notes           text,
    created_at      timestamptz    not null default now(),
    updated_at      timestamptz    not null default now(),
    constraint uq_payments_consultation unique (consultation_id)
);
create index if not exists ix_payments_user_date  on public.payments (user_id, payment_date);
create index if not exists ix_payments_patient_id on public.payments (patient_id);

create table if not exists public.clinical_records (
    id              serial primary key,
    user_id         integer     not null references public.users (id) on delete cascade,
    patient_id      integer     not null references public.patients (id) on delete cascade,
    consultation_id integer     references public.consultations (id) on delete set null,
    session_date    date        not null,
    content         text        not null,  -- criptografado (Fernet) pelo app
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now()
);
create index if not exists ix_clinical_records_user_id         on public.clinical_records (user_id);
create index if not exists ix_clinical_records_patient_id      on public.clinical_records (patient_id);
create index if not exists ix_clinical_records_consultation_id on public.clinical_records (consultation_id);

create table if not exists public.working_hours (
    id         serial primary key,
    user_id    integer not null references public.users (id) on delete cascade,
    weekday    integer not null check (weekday between 0 and 6),  -- 0 = segunda
    start_time time    not null,
    end_time   time    not null,
    active     boolean not null default true
);
create index if not exists ix_working_hours_user_id on public.working_hours (user_id);

create table if not exists public.blocked_periods (
    id         serial primary key,
    user_id    integer not null references public.users (id) on delete cascade,
    start_date date    not null,
    end_date   date    not null,
    reason     varchar(255)
);
create index if not exists ix_blocked_periods_user_id on public.blocked_periods (user_id);

create table if not exists public.audit_logs (
    id         serial primary key,
    user_id    integer references public.users (id) on delete set null,
    action     varchar(255) not null,
    target     varchar(255),
    created_at timestamptz  not null default now()
);
create index if not exists ix_audit_logs_user_id on public.audit_logs (user_id);

-- ------------------------------------------------- bloqueio da API pública
do $$
declare
    t text;
begin
    foreach t in array array[
        'users', 'patients', 'consultations', 'payments', 'clinical_records',
        'working_hours', 'blocked_periods', 'audit_logs'
    ] loop
        execute format('alter table public.%I enable row level security', t);
        execute format('revoke all on table public.%I from anon, authenticated', t);
    end loop;
end $$;

revoke usage, select on all sequences in schema public from anon, authenticated;
