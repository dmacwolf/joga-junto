#!/usr/bin/env python3
"""Guarda a chave da Steam nos segredos do Supabase sem mostrar a chave na tela.

Uso: python tools/definir_chave_steam.py
"""
import getpass
import re
import subprocess
import sys

PROJETO = 'mlfxwdfuadcactwwbjyl'

chave = getpass.getpass('Cole a chave da Steam e aperte Enter (nada aparece na tela): ').strip()
if not re.fullmatch(r'[0-9A-Fa-f]{32}', chave):
    sys.exit('Essa chave não parece certa: ela tem 32 letras e números. Nada foi guardado.')

npx = 'npx.cmd' if sys.platform == 'win32' else 'npx'
resultado = subprocess.run(
    [npx, '--yes', 'supabase@3.0.0', 'secrets', 'set', f'STEAM_KEY={chave}', '--project-ref', PROJETO, '--yes'],
    capture_output=True, text=True, errors='replace',
)
if resultado.returncode != 0:
    sys.exit('Não consegui guardar a chave. Avise o Claude.')
print('Chave guardada com sucesso. Pode voltar para a conversa.')
