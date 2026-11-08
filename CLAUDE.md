# Joga Junto: contexto do projeto

App estilo "Tinder de jogo" para brasileiros encontrarem jogadores com gosto parecido e fazerem amizade.
Foi criado numa sessão do Claude na web e levado para cá. O dono escreve em português; responda em português.

## O que o app faz hoje

Uma página única (HTML, CSS e JS puro, sem build), visual de HUD gamer (escuro, neon ciano e magenta, cantos cortados).
Abas: **Descobrir** (swipe de cards), **Matches** (conversa com assuntos prontos), **Buscar** (digita um jogo e vê
jogadores por similaridade de jogos), **Jogos** (nota de 1 a 5, uma linha, compartilhar), **Perfil**.

Decisões de produto que o dono pediu e devem continuar valendo:
- O card do jogador **não usa foto**. Mostra jogos favoritos, ritmo (barra casual a competitivo), objetivos em
  ordem de prioridade (amizade, competir, sem pressão, papo profundo, papo leve) e se curte música.
- A afinidade pesa: jogos em comum 30%, objetivos em comum e ordem 30%, ritmo 15%, gêneros 10%, música 10%, horário 5%.
- A busca por jogo mede similaridade por características (gênero, 2D, difícil, co-op, competitivo etc.). "Quanto mais
  parecido, melhor" ordena a lista.
- Nome: **Joga Junto**. Logo: "JJ" imitando joystick (duas letras j com bolas no lugar do pingo, uma ciano e uma magenta).

## Estado real, sem enfeite

- Os 12 jogadores e as respostas das conversas são **dados de exemplo e simulados**. Não há contas, servidor nem
  banco. Perfil, notas, curtidas e matches ficam no `localStorage` do navegador (chave `player2-v2`, mantida de
  propósito para não apagar dados já salvos).
- Para ter pessoas reais se encontrando, o próximo passo grande é um backend compartilhado (contas, perfis, matches,
  mensagens). Ainda não foi decidido qual (Supabase foi cogitado).

## Estrutura

- `source/artifact.html`: **fonte de verdade do app**. Edite este arquivo.
- `tools/make_web.py`: gera `web/index.html` a partir do source. Rode `python3 tools/make_web.py` depois de editar.
- `web/`: site publicado (`index.html` é gerado, `sw.js` é o service worker com rede primeiro e cache de reserva).
- `android/`: casca Android em WebView que abre o site publicado em tela cheia. Pacote `app.jogajunto`,
  `versionCode` vem de `GITHUB_RUN_NUMBER`, URL do site entra por `-PappUrl=...`.
- `.github/workflows/pages.yml` publica `web/` no GitHub Pages; `apk.yml` compila o APK e o põe em Releases (`apk-latest`).
- Chave de assinatura do APK: fica nos segredos do GitHub (`KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`) e, neste PC, em
  `android/keystore/jogajunto.jks`, ignorada pelo git. Nunca enviar a chave nem escrever a senha no repositório.

## Repositório

Fica na conta `dmacwolf` do GitHub: `dmacwolf/joga-junto`. Este PC pode ter outra conta ativa no `gh`; não troque a
conta ativa. O `git push` desta pasta já usa a dmacwolf (configuração local). Para comandos `gh`, use
`GH_TOKEN=$(gh auth token --user dmacwolf) gh ... -R dmacwolf/joga-junto`.

Como o APK só abre o site publicado, mudanças no app (`source/artifact.html`, depois `make_web.py`, depois push)
chegam ao celular sem reinstalar. O APK só muda se a pasta `android/` mudar.

## Armadilhas já conhecidas

- A versão que o Claude publicou como artefato (claude.ai/artifact) tem um `<title>`, `<meta>` e `<style>` soltos no
  topo, sem `<html>`. O `make_web.py` já trata isso. Se editar o topo do source, mantenha o marcador `<div class="fx"`.
- As 5 abas inferiores ficam apertadas em telas de 360px. Teste em celular pequeno.
- Foi validada só a sintaxe do JavaScript e a compilação do Java contra stubs. O layout em celular real não foi conferido.
