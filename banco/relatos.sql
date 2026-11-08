-- Erros do APK, enviados pelo próprio app quando ele fecha sozinho. Só o dono do projeto lê.

create table if not exists private.relatos_app (
  id bigint generated always as identity primary key,
  criado_em timestamptz not null default now(),
  versao text,
  aparelho text,
  texto text not null
);

alter table private.relatos_app enable row level security;

create or replace function public.jj_relato_app(versao text, aparelho text, texto text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  if (select count(*) from private.relatos_app where criado_em > now() - interval '1 hour') >= 100 then
    return;
  end if;
  insert into private.relatos_app (versao, aparelho, texto)
  values (left(versao, 40), left(aparelho, 120), left(coalesce(texto, ''), 8000));
end;
$$;

revoke all on function public.jj_relato_app(text, text, text) from public, anon, authenticated;
grant execute on function public.jj_relato_app(text, text, text) to anon, authenticated;
