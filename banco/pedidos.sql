-- Pedidos de alteração que o cliente escreve dentro do app.
-- As tabelas ficam num schema que a internet não alcança. O app só fala com as três funções jj_*.
-- O código de acesso fica guardado como hash em private.config, nunca em texto puro.

create schema if not exists private;
revoke all on schema private from public, anon, authenticated;

create table if not exists private.config (
  chave text primary key,
  valor text not null
);

create table if not exists private.pedidos (
  id bigint generated always as identity primary key,
  criado_em timestamptz not null default now(),
  texto text not null check (char_length(texto) between 1 and 4000),
  status text not null default 'novo' check (status in ('novo', 'fazendo', 'feito', 'recusado')),
  resposta text,
  atualizado_em timestamptz
);

alter table private.config enable row level security;
alter table private.pedidos enable row level security;

create or replace function private.codigo_valido(codigo text)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1 from private.config
    where chave = 'codigo_cliente_hash'
      and valor = encode(extensions.digest(upper(trim(coalesce(codigo, ''))), 'sha256'), 'hex')
  );
$$;

create or replace function public.jj_codigo_ok(codigo text)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select private.codigo_valido(codigo);
$$;

create or replace function public.jj_enviar_pedido(codigo text, texto text)
returns bigint
language plpgsql
security definer
set search_path = ''
as $$
declare
  limpo text := trim(coalesce(texto, ''));
  novo_id bigint;
begin
  if not private.codigo_valido(codigo) then
    raise exception 'codigo_invalido';
  end if;
  if char_length(limpo) = 0 or char_length(limpo) > 4000 then
    raise exception 'texto_invalido';
  end if;
  if (select count(*) from private.pedidos where criado_em > now() - interval '1 hour') >= 60 then
    raise exception 'limite';
  end if;
  insert into private.pedidos (texto) values (limpo) returning id into novo_id;
  return novo_id;
end;
$$;

create or replace function public.jj_pedidos(codigo text)
returns table (id bigint, criado_em timestamptz, texto text, status text, resposta text)
language plpgsql
stable
security definer
set search_path = ''
as $$
begin
  if not private.codigo_valido(codigo) then
    raise exception 'codigo_invalido';
  end if;
  return query
    select p.id, p.criado_em, p.texto, p.status, p.resposta
    from private.pedidos p
    order by p.id desc
    limit 100;
end;
$$;

revoke all on function private.codigo_valido(text) from public, anon, authenticated;
revoke all on function public.jj_codigo_ok(text) from public, anon, authenticated;
revoke all on function public.jj_enviar_pedido(text, text) from public, anon, authenticated;
revoke all on function public.jj_pedidos(text) from public, anon, authenticated;
grant execute on function public.jj_codigo_ok(text) to anon, authenticated;
grant execute on function public.jj_enviar_pedido(text, text) to anon, authenticated;
grant execute on function public.jj_pedidos(text) to anon, authenticated;
