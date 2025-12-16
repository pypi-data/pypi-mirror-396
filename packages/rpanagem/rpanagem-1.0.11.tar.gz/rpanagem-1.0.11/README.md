# RPANAGEM

![Status](https://img.shields.io/badge/status-experimental-orange)
![License](https://img.shields.io/badge/license-MIT-blue)

Utilitário Python para automações e rotinas da Nagem. Criado para facilitar processos internos com foco em clareza, modularidade e reutilização.

## Objetivos do pacote
1. Incentivar o reuso;
2. Oferecer maior segurança ao desenvolvedor;
3. Tornar sua vida mais produtiva e fácil :)

Atenção: lembre-se de incrementar a versão e atualizar toda a documentação antes de gerar um novo pacote.

---

## ⚙️ Funcionalidades disponíveis no momento
1. 📈 conexao_banco
    - conectar_odbc
    - executar_select
    - conectar_sqlserver
    - executar_update_insert
    - atualizar_monitoramento
2. 📤 enviar_email
    - conectar_smtp_server
    - enviar_email
3. 📅 manipula_datahora
    - obter_incluir_valor_data
    - converter_data
    - data_hora_para_binario
    - binario_para_data_hora
    - obter_ultimo_dia_do_mes
    - obter_dia_da_semana
4. 📁📝 manipula_diretorios_arquivos
    - arquivos_existem
    - criar_arquivo
    - criar_xlsx_com_colunas
    - inserir_tabela_xlsx
    - formatar_xlsx
    - criar_logger_diario
    - mover_arquivo
    - copiar_arquivo
    - detectar_encoding
    - ler_csv
    - obter_arquivos
    - ler_txt
    - obter_infomacoes_arquivo
    - alterar_valor_celula_vazia_xlsx
    - alterar_valor_celula_xlsx_com_condicao
    - ler_xlsx
    - converter_para_base64
    
    - diretorio_existe
    - criar_diretorio
    - limpar_diretorio
5. 🧩 manipula_sap
    - fechar_sap_se_aberto
    - start_sap_logon
    - procurar_campos
    - procurar_janela
    - verificar_mensagem_status
    - fechar_sessao_sap
    - run_transaction
    - anexar_sessao_sap
6. ⚙️ manipula_conagem
    - iniciar
    - fechar_conagem_se_existir
    - find_control
    - clicar_btn
    - inserir_texto
    - login
    - obter_controles_janela
    - selecionar_empresa
    - digitar_modulo_tela_principal
    - procurar_obter_janela_principal
    - acessar_subjanela
    - procurar_subjanela_mdiclient
    - clicar_botao
    - fechar_popup
    - selecionar_combobox
    - extrair_relatorio_rpa_faturamento_corel93d
    - extrair_relatorio_rpa
    - fechar_aplicacao
7. 🖥️ manipula_navegador
    - iniciar_driver_chrome
    - fazer_login
    - gerar_pdf_pagina
    - localizar_elemento
    - buscar_texto_no_dom
    - clicar_elemento
    - digitar_elemento
    - selecionar_tag_select
    - selecionar_checkbox
    - voltar_contexto_principal
    - verificar_tipo_elemento
    - procurar_elemento_iframe
    - obter_nova_janela_navegador
    - voltar_janela_principal
    - finalizar


## 🚀 Instalação com poetry
    poetry add rpanagem


## 🚀 Instalação com pip
    pip install rpanagem



## Dúvidas?
Entre em contato com eduarda.lima@nagem.com.br ou desenvolvimentorpa@nagem.com.br.
