-- Conexão com a Steam. Como o app ainda não tem contas, cada aparelho guarda um token secreto
-- e aqui fica só o hash dele. A função de servidor `steam` grava; o app só lê e apaga a própria conexão.

create table if not exists private.steam_conexoes (
  token_hash text primary key,
  steamid text not null,
  nome text,
  avatar text,
  perfil text,
  privado boolean not null default false,
  total_jogos integer not null default 0,
  total_horas integer not null default 0,
  jogos jsonb not null default '[]'::jsonb,
  criado_em timestamptz not null default now()
);

alter table private.steam_conexoes enable row level security;

create or replace function public.jj_steam_salvar(
  p_hash text, p_steamid text, p_nome text, p_avatar text, p_perfil text,
  p_privado boolean, p_total_jogos integer, p_total_horas integer, p_jogos jsonb
)
returns void
language sql
security definer
set search_path = ''
as $$
  insert into private.steam_conexoes (token_hash, steamid, nome, avatar, perfil, privado, total_jogos, total_horas, jogos)
  values (p_hash, p_steamid, p_nome, p_avatar, p_perfil, p_privado, p_total_jogos, p_total_horas, p_jogos);
$$;

create or replace function public.jj_steam_dados(token text)
returns jsonb
language sql
stable
security definer
set search_path = ''
as $$
  select jsonb_build_object('nome', c.nome, 'avatar', c.avatar, 'perfil', c.perfil, 'privado', c.privado,
                            'total_jogos', c.total_jogos, 'total_horas', c.total_horas, 'jogos', c.jogos)
  from private.steam_conexoes c
  where c.token_hash = encode(extensions.digest(coalesce(token, ''), 'sha256'), 'hex');
$$;

create or replace function public.jj_steam_apagar(token text)
returns void
language sql
security definer
set search_path = ''
as $$
  delete from private.steam_conexoes
  where token_hash = encode(extensions.digest(coalesce(token, ''), 'sha256'), 'hex');
$$;

revoke all on function public.jj_steam_salvar(text, text, text, text, text, boolean, integer, integer, jsonb) from public, anon, authenticated;
revoke all on function public.jj_steam_dados(text) from public, anon, authenticated;
revoke all on function public.jj_steam_apagar(text) from public, anon, authenticated;
grant execute on function public.jj_steam_salvar(text, text, text, text, text, boolean, integer, integer, jsonb) to service_role;
grant execute on function public.jj_steam_dados(text) to anon, authenticated;
grant execute on function public.jj_steam_apagar(text) to anon, authenticated;
