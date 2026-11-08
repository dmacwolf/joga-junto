# Joga Junto

App para encontrar jogadores por gosto de jogo, objetivos e ritmo.

## Como as peças se encaixam

- `source/artifact.html`: a versão do app como o Claude a publica.
- `tools/make_web.py`: transforma essa versão em `web/index.html`, uma página independente.
- `web/`: o site. O GitHub Pages publica esta pasta a cada mudança (workflow `pages.yml`).
- `android/`: o APK. É uma casca que abre o site em tela cheia (workflow `apk.yml`).

Como o APK sempre abre o site publicado, **mudanças no app aparecem sem instalar nada de novo**.
O APK só precisa ser reinstalado se a casca Android mudar.

## Ativar uma vez

1. No repositório, vá em Settings > Pages e escolha "Source: GitHub Actions".
2. Em Actions, rode "Publicar o app (site)" e "Gerar o APK" (ou faça qualquer push).
3. O APK fica em Releases, na versão `apk-latest`: `jogajunto.apk`.

## Instalar no Android

Abra o link do `jogajunto.apk` no celular, baixe e permita "instalar apps desconhecidos" para o navegador.

## Nota sobre a assinatura

O APK é assinado com uma chave própria, guardada nos segredos do GitHub (`KEYSTORE_BASE64` e `KEYSTORE_PASSWORD`).
Ela não fica no repositório. Usar sempre a mesma chave é o que permite a cada APK novo atualizar o anterior.
