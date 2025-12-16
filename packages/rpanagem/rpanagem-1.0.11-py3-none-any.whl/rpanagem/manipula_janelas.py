"""
app_automator.py

Classe AppAutomator — automatiza abertura/conexão à janela de um app e efetua login.
Suporta backend principal pywinauto (Windows) e fallback pyautogui (image-based).

Requisitos (instalar separadamente):
    pip install pywinauto pyautogui pillow opencv-python

Observações de segurança:
    - Não guarde senhas em texto claro. Prefira keyring ou variáveis de ambiente.
    - Se o app roda elevado (admin), execute o script com privilégios compatíveis.
"""

from __future__ import annotations
import time
import logging
import os
from typing import Optional, Tuple, Dict, Any, Union
from contextlib import AbstractContextManager

from pywinauto.timings import TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto import Application, Desktop
import json
import win32gui
import win32process
import pyautogui

# Tipo para especificadores de controle usados por pywinauto: (property_name, value)
ControlSpec = Tuple[str, str]


from rpanagem import manipula_diretorios_arquivos
import logging
logger = logging.getLogger(__name__)
log = manipula_diretorios_arquivos.Arquivos()
module_logger = log.criar_logger_diario("./log", nome_arquivo_log="manipula_janelas.log", logger=logger)


class Janela():
    """..."""
    def __init__(self,):
        """..."""
        self.app = None 
        self.janela = None  # janela alvo 

    def fechar_janela(self, titulo: str, classe: str):
        """..."""
        try:
            # Desktop() Permite acessar qualquer janela visível no Windows, mesmo que você não tenha iniciado o app via Application.

            # for w in Desktop(backend="uia").windows():
            #     title = w.window_text()
            #     if titulo in title:
            #         w.close()
            #     print(title)
            module_logger.info(f"Verificando Janela '{titulo}'...")
            try:
                self.janela = Desktop(backend="uia").window(title_re=titulo)
            except:
                self.janela = Desktop(backend="win32").window(title_re=titulo)

            self.janela.close()
            module_logger.info("✅  Janela fechada")
            return True
        except Exception:
            module_logger.info(f"Janela '{titulo}' não encontrada")
            return False


