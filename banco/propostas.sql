-- Propostas publicadas dentro de um pedido do cliente. Ele vê, aprova uma ou pede mudança.
-- `imagem` é o caminho do arquivo dentro do site (por exemplo, propostas/logo-1.svg).
-- Só o dono do projeto insere propostas: o app não tem nenhuma função para isso.

create table if not exists private.propostas (
  id bigint generated always as identity primary key,
  pedido_id bigint not null references private.pedidos (id) on delete cascade,
  criado_em timestamptz not null default now(),
  titulo text not null,
  descricao text,
  imagem text not null,
  status text not null default 'aberta' check (status in ('aberta', 'aprovada', 'mudanca', 'nao_escolhida')),
  comentario text,
  respondido_em timestamptz
);

alter table private.propostas enable row level security;

-- Propostas com status 'descartada' ficam na pasta Descartadas, só para consulta.
alter table private.propostas drop constraint if exists propostas_status_check;
alter table private.propostas add constraint propostas_status_check
  check (status in ('aberta', 'aprovada', 'mudanca', 'nao_escolhida', 'descartada'));

create or replace function public.jj_propostas(codigo text)
returns table (id bigint, pedido_id bigint, titulo text, descricao text, imagem text, status text, comentario text)
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
    select p.id, p.pedido_id, p.titulo, p.descricao, p.imagem, p.status, p.comentario
    from private.propostas p
    order by p.id;
end;
$$;

create or replace function public.jj_responder_proposta(codigo text, proposta bigint, acao text, nota text default '')
returns text
language plpgsql
security definer
set search_path = ''
as $$
declare
  alvo private.propostas%rowtype;
  limpa text := trim(coalesce(nota, ''));
begin
  if not private.codigo_valido(codigo) then
    raise exception 'codigo_invalido';
  end if;
  select * into alvo from private.propostas where id = proposta for update;
  if not found then
    raise exception 'proposta_inexistente';
  end if;
  if alvo.status = 'descartada' then
    raise exception 'descartada';
  end if;
  if exists (select 1 from private.propostas where pedido_id = alvo.pedido_id and status = 'aprovada') then
    raise exception 'ja_aprovada';
  end if;

  if acao = 'aprovar' then
    update private.propostas set status = 'aprovada', respondido_em = now() where id = alvo.id;
    update private.propostas set status = 'nao_escolhida', respondido_em = now()
      where pedido_id = alvo.pedido_id and id <> alvo.id and status <> 'descartada';
    update private.pedidos
      set resposta = 'Você aprovou: ' || alvo.titulo || '. Agora falta aplicar no app.', atualizado_em = now()
      where id = alvo.pedido_id;
    return 'aprovada';
  elsif acao = 'mudar' then
    if char_length(limpa) = 0 or char_length(limpa) > 2000 then
      raise exception 'texto_invalido';
    end if;
    update private.propostas
      set status = 'mudanca',
          comentario = case when comentario is null then limpa else comentario || E'\n' || limpa end,
          respondido_em = now()
      where id = alvo.id;
    return 'mudanca';
  end if;

  raise exception 'acao_invalida';
end;
$$;

revoke all on function public.jj_propostas(text) from public, anon, authenticated;
revoke all on function public.jj_responder_proposta(text, bigint, text, text) from public, anon, authenticated;
grant execute on function public.jj_propostas(text) to anon, authenticated;
grant execute on function public.jj_responder_proposta(text, bigint, text, text) to anon, authenticated;
