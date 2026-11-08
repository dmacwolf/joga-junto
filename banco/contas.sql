-- Contas de verdade (login pelo Google, via Supabase Auth).
-- Cada pessoa só alcança a própria linha: as funções usam auth.uid().

create table if not exists private.contas (
  user_id uuid primary key references auth.users (id) on delete cascade,
  nascimento date not null,
  estado jsonb not null default '{}'::jsonb,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

alter table private.contas enable row level security;

create or replace function public.jj_conta_ler()
returns jsonb
language sql
stable
security definer
set search_path = ''
as $$
  select c.estado from private.contas c where c.user_id = auth.uid();
$$;

create or replace function public.jj_conta_criar(nascimento date, estado jsonb)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if auth.uid() is null then
    raise exception 'sem_sessao';
  end if;
  if nascimento > (current_date - interval '18 years')::date then
    raise exception 'menor';
  end if;
  if octet_length(estado::text) > 200000 then
    raise exception 'grande';
  end if;
  insert into private.contas (user_id, nascimento, estado)
  values (auth.uid(), nascimento, estado)
  on conflict (user_id) do nothing;
end;
$$;

create or replace function public.jj_conta_salvar(estado jsonb)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if auth.uid() is null then
    raise exception 'sem_sessao';
  end if;
  if octet_length(estado::text) > 200000 then
    raise exception 'grande';
  end if;
  update private.contas c set estado = jj_conta_salvar.estado, atualizado_em = now() where c.user_id = auth.uid();
end;
$$;

create or replace function public.jj_conta_apagar()
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if auth.uid() is null then
    raise exception 'sem_sessao';
  end if;
  delete from auth.users where id = auth.uid();
end;
$$;

revoke all on function public.jj_conta_ler() from public, anon, authenticated;
revoke all on function public.jj_conta_criar(date, jsonb) from public, anon, authenticated;
revoke all on function public.jj_conta_salvar(jsonb) from public, anon, authenticated;
revoke all on function public.jj_conta_apagar() from public, anon, authenticated;
grant execute on function public.jj_conta_ler() to authenticated;
grant execute on function public.jj_conta_criar(date, jsonb) to authenticated;
grant execute on function public.jj_conta_salvar(jsonb) to authenticated;
grant execute on function public.jj_conta_apagar() to authenticated;
