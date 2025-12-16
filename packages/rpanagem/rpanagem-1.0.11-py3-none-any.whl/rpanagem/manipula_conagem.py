import time
from typing import Optional, Tuple
from pywinauto.timings import TimeoutError
from pywinauto.findwindows import ElementNotFoundError
from pywinauto import Application
import pyautogui

from rpanagem import manipula_diretorios_arquivos
import logging
logger = logging.getLogger(__name__)
log = manipula_diretorios_arquivos.Arquivos()
module_logger = log.criar_logger_diario("./log", nome_arquivo_log="manipula_conagem.log", logger=logger)

# Tipo para especificadores de controle usados por pywinauto: (property_name, value)
ControlSpec = Tuple[str, str]


class AutomationError(Exception):
    """Erro genérico de automação."""
    pass


class Conagem():
    """Controla a Gui do programa conagem."""

    def __init__(self, default_timeout: float = 120.0) -> None:
        """
        Iniciando variáveis.

        :param default_timeout: tempo (segundos) para aguardar janelas/controles.
        """
        self.backend = "uia"  # backend para pywinauto: 'uia' (recomendado) ou 'win32'.
        self.default_timeout = default_timeout

        # preenchidos quando conectar/iniciar
        self.app = None  # objeto Application do pywinauto (se usado)
        self.janela = None  # janela alvo (pywinauto wrapper)
        self.programa_conectado = False

    def iniciar(self, caminho_executavel = None) -> None:
        """
        Inicia um executável do programa.

        :param caminho_executavel: caminho para o executável. Se None, tenta conectar apenas pela janela (titulo_janela).
        :type caminho_executavel: str

        :returns: Instancia do programa executado.
        :rtype: pywinauto.Application
        """
        try:
            if not caminho_executavel:
                raise ValueError("Parametro 'caminho_executavel' não foi fornecido.")

            module_logger.info("Iniciando executável: %s", caminho_executavel)
            self.app = Application(backend=self.backend).start(cmd_line=caminho_executavel, timeout=self.default_timeout)
            
            # self.obter_janela()
            self.programa_conectado = True
            module_logger.info("✅  Conectado usando pywinauto (backend=%s).", self.backend)

            # module_logger.info(f"Janelas encontradas: {self.app.windows()}")

            if self.app.window(title="Selecione o Alias:").exists():
                module_logger.info("Janela 'Selecione o Alias:' encontrada")

                self.janela = self.app.window(title_re="Selecione o Alias:")


                try:
                    self.janela.wait("visible", timeout=5)
                    self.janela.set_focus()
                    module_logger.info("✅  Janela 'Selecione o Alias' encontrada e ativa.")
                except Exception as erro:
                    raise Exception(f"❌  Erro ao visualizar e ativar a janela 'Selecione o Alias': {erro}")

                # self.janela.print_control_identifiers()
                # info_controles = self.obter_controles_janela()
                # print(info_controles)

                # self.janela.child_window(class_name="TComboBox").select('NAG9999')

                self.clicar_btn(
                    botao_ctrl=('class_name', 'TBitBtn'),
                )

                module_logger.info("✅  Alias selecionado")
            else:
                pass
            
            return self.app

        except Exception as exc:
            module_logger.error("❌  Falha ao iniciar programa via pywinauto:")
            self.app = None
            self.programa_conectado = False
            raise Exception("❌  Falha ao iniciar programa via pywinauto.")

    def fechar_conagem_se_existir(self):
        """Verifica se o programa esta aberto e fecha-o."""
        module_logger.info("Conectando e fechando a janela principal: Sistema Comercial Nagem...")
        try:
            self.app = Application(backend='win32').connect(title_re=".*Sistema Comercial Nagem.*", class_name='TfCONagem0')
        except:
            try:
                self.app = Application(backend='uia').connect(title_re=".*Sistema Comercial Nagem.*", class_name='TfCONagem0')
            except ElementNotFoundError:
                pass
        
        if self.app is not None:
            self.app.kill()

    def find_control(self, ctrl_spec: Optional[ControlSpec], timeout: float = 5.0):
        """
        Localiza um controle pela especificação (property, value).

        :param ctrl_spec: Tupla ('automation_id' | 'title' | 'name', valor).
        :param timeout: Tempo máximo de espera pelo controle.
        :return: Wrapper do controle ou None se não encontrado.
        """
        if not self.janela or not ctrl_spec:
            return None

        prop, val = ctrl_spec
        kwargs = {prop: val}
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                ctrl = self.janela.child_window(**kwargs).wrapper_object()
                if ctrl.is_enabled() and ctrl.is_visible():
                    module_logger.info("Controle localizado: %s=%s", prop, val)
                    return ctrl
            except Exception:
                pass
            time.sleep(0.5)

        module_logger.warning("Controle não encontrado: %s=%s", prop, val)
        return None

    def clicar_btn(self, botao_ctrl: Optional[ControlSpec]) -> bool:
        """
        Retorna True se as ações foram executadas.

        :param botao_ctrl: child_window do botão que se deseja clicar.
        :type botao_ctrl: tuple(str, str)
        """
        if not self.janela:
            raise AutomationError("Janela alvo não conectada para pywinauto.")

        clicado = False

        module_logger.info("Tentando localizar botões...")
        b_ctrl = self.find_control(botao_ctrl) if botao_ctrl else None

        # clicar
        if b_ctrl is not None:
            module_logger.info("Clicando no botão...")
            try:
                b_ctrl.click_input()
                clicado = True
            except Exception:
                try:
                    b_ctrl.invoke()
                    clicado = True
                except Exception:
                    module_logger.warning("❌  Não foi possível clicar/invocar o botão.")
        else:
            # heurística por texto em botões
            module_logger.debug("Tentando heurística para botão...")
            try:
                buttons = self.janela.descendants(control_type="Button")
                for b in buttons:
                    try:
                        text = b.window_text().lower()
                        if any(k in text for k in ("entrar", "login", "logar", "ok", "aceitar", "submit", "rpa")):
                            module_logger.info("Clicando botão identificado com texto '%s'", text)
                            b.click_input()
                            clicado = True
                            break
                    except Exception:
                        continue
            except Exception:
                module_logger.debug("Heurística de botões falhou.")

        if clicado is True:
            module_logger.info("✅  Botão clicado")
            return True
        else:
            module_logger.info("❌  Não foi possível clicar no botão.")
            return False

    def inserir_texto(self, control, text: str) -> None:
        """
        Tenta formas seguras de inserir texto no controle pywinauto.
        """
        try:
            # set_edit_text quando disponível (mais rápido e confiável)
            control.set_edit_text(text)
            return
        except Exception:
            pass

        try:
            # fallback para typing (mais lento)
            control.type_keys(text, with_spaces=True, set_foreground=True)
        except Exception as exc:
            module_logger.exception("Falha ao inserir texto no controle: %s", exc)
            raise

    def login(
        self,
        usuario: str,
        senha: str,
        # usuario_ctrl: Optional[ControlSpec] = None,
        # senha_ctrl: Optional[ControlSpec] = None,
        # botao_ctrl: Optional[ControlSpec] = None,
    ) -> bool:
        """
        Loga no sistema com usuario e senha.
        Retorna True se as ações foram executadas (não verifica resultado no servidor).
        """
        module_logger.info("____________LOGIN CONAGEM______________")
        module_logger.info("Aguardando janela de login ficar visível...")
        
        if self.app.window(title="Validação de Usuário").wait('exists enabled visible ready', timeout=self.default_timeout):
            module_logger.info("Janela de login encontrada")

            self.janela = self.app.window(title_re=f"Validação de Usuário")
        else:
            self.janela = None
            module_logger.info(f"❌ Janela não encontrada. Erro: {erro}")
            raise Exception(f"❌ Janela de login não encontrada. Erro: {erro}")

        # ----------------------------------------------------------------

        try:
            module_logger.info("Tentando localizar controles dos campos...")

            # self.janela.print_control_identifiers()
            info_controles = self.obter_controles_janela()
            resultado_edit = [ctrl for ctrl in info_controles if ctrl['class_name'].lower() == 'tedit' and ctrl['control_type'] == 'Edit']

            # nesse caso o edit 1 é o campo da senha e o 2 é o do usuario
            if not resultado_edit:
                self.logger.info("❌  Nenhum campo 'Edit' encontrado na tela de login")
                raise Exception("❌  Nenhum campo 'Edit' encontrado na tela de login")

            resultado_botao_ok = next(
                (ctrl for ctrl in info_controles if ctrl['name'].lower() == 'ok' and ctrl['control_type'] == 'Button'),
                None
            )  # retorna o primeiro dicionário que atende ao filtro, ou None se nenhum atender.

            if resultado_botao_ok is None:
                self.logger.info("❌  Nenhum campo 'Button - ok' encontrado na tela de login")
                raise Exception("❌  Nenhum campo 'Button - ok' encontrado na tela de login")
            
            usuario_ctrl = ('auto_id', resultado_edit[2]['auto_id'])
            senha_ctrl = ('auto_id', resultado_edit[1]['auto_id'])
            botao_ctrl = ('auto_id', resultado_botao_ok['auto_id'])

        except Exception as erro:
            self.janela = None
            module_logger.info(f"❌ Erro ao localizar controles da janela de login. Erro: {erro}")
            raise Exception(f"❌ Erro ao localizar controles da janela de login. Erro: {erro}")

        # ----------------------------------------------------------------

        # inserir usuario
        u_ctrl = self.find_control(usuario_ctrl) if usuario_ctrl else None
        if u_ctrl is None:
            module_logger.warning("Controle usuário não encontrado.")
        else:
            module_logger.info("Inserindo usuário...")
            self.inserir_texto(u_ctrl, usuario)
        

        # inserir senha
        s_ctrl = self.find_control(senha_ctrl) if senha_ctrl else None
        if s_ctrl is None:
            module_logger.warning("Controle senha não encontrado.")
        else:
            module_logger.info("Inserindo senha...")
            self.inserir_texto(s_ctrl, senha)


        # clicar em OK
        b_ctrl = self.find_control(botao_ctrl) if botao_ctrl else None
        self.clicar_btn(
                botao_ctrl=botao_ctrl,
            )

        module_logger.info(f"u_ctrl: {u_ctrl}")
        module_logger.info(f"s_ctrl: {s_ctrl}")
        module_logger.info(f"b_ctrl: {b_ctrl}")

        # fallback heurístico: pegar edits se não foram fornecidos
        try:
            if (u_ctrl is None or s_ctrl is None):
                edits = self.janela.descendants(control_type="Edit")
                module_logger.info(f"Edit encontrados: {edits}")

                if edits:
                    # tenta atribuir por ordem
                    if u_ctrl is None and len(edits) >= 1:
                        u_ctrl = edits[0]
                    if s_ctrl is None and len(edits) >= 2:
                        s_ctrl = edits[1]
        except Exception:
            # não crítico; continua
            module_logger.debug("Heurística edits falhou ou não aplicável.")

        module_logger.info("✅  Login conagem realizado com sucesso:")

        return True

    def obter_controles_janela(self):
        """
        Obtem os controles de uma janela.

        :returns: Os dados o controle ou uma mensagem generica caso contrário.
        :rtype: list or str
        """
        controls_info = []
        for ctrl in self.janela.descendants():
            try:
                ctrl_info = {
                    "auto_id": ctrl.element_info.automation_id,
                    "name": ctrl.element_info.name,
                    "control_type": ctrl.element_info.control_type,
                    "class_name": ctrl.element_info.class_name,
                }
                controls_info.append(ctrl_info)
            except Exception as e:
                module_logger.error(f"❌  Falha ao obter controles da janela: {e}")
                raise Exception(f"❌  Falha ao obter controles da janela: {e}")

        module_logger.info(f"{len(controls_info)} controles encontrados na janela")
        return controls_info if controls_info else "nenhum controle encontrado"

    def selecionar_empresa(self, nome_empresa: str = "0001 CD REC - RECIFE"):
        """
        Seleciona uma empresa na janela 'Selecione a Empresa [Módulo: Empresa]'
        e confirma com o botão OK.

        :param nome_empresa: Texto exato ou parcial exibido no combobox.
        :type nome_empresa: str
        """
        # module_logger.info("Conectando a janela principal: Sistema Comercial Nagem...")
        # self.app = Application(backend=self.backend).connect(title_re="Sistema Comercial Nagem.*")

        module_logger.info("Procurando a janela 'Selecione a Empresa'...")
        try:
            self.janela = self.app.window(title_re="Selecione a Empresa.*Módulo: Empresa", class_name="TfEmpresa")
        except Exception as erro:
            raise Exception(f"❌  Erro ao obter janela 'Selecione a Empresa': {erro}")
        

        try:
            self.janela.wait("visible", timeout=5)
            self.janela.set_focus()
            module_logger.info("✅  Janela 'Selecione a Empresa' encontrada e ativa.")
        except Exception as erro:
            raise Exception(f"❌  Erro ao visualizar e ativar janela: {erro}")


        module_logger.info("Selecionando empresa no combobox: %s", nome_empresa)
        try:
            combobox = self.janela.child_window(class_name="TComboBox")
            combobox.select(nome_empresa)
        except Exception:
            try:
                # se o texto não casar exatamente, tenta por typing
                combobox.type_keys(nome_empresa)
                time.sleep(0.3)
            except Exception as erro:
                raise Exception(f"❌  Erro ao selecionar empresa: {erro}")


        module_logger.info("Clicando no botão OK...")
        try:
            btn_ok = self.janela.child_window(title_re=".*OK.*", class_name="TBitBtn")
            btn_ok.click_input()
            self.procurar_obter_janela_principal()
        except Exception as erro:
            raise Exception(f"❌  Erro ao clicar no botão 'OK': {erro}")

        module_logger.info("✅ Empresa selecionada e confirmada com sucesso.")

    def digitar_modulo_tela_principal(self, modulo: str):
        """Verifica na janela principal e digita o nome do modulo.

        :param modulo: Nome do modulo. Ex.: COREL967
        :type modulo: str
        """
        self.janela = self.procurar_obter_janela_principal()

        if self.janela.wait('exists enabled visible ready', timeout=self.default_timeout):
            # Traz a janela para o primeiro plano
            self.janela.wait("visible", timeout=self.default_timeout)
            self.janela.set_focus()
            # self.janela.restore()
            # self.janela.set_keyboard_focus()

            # Obter a resolução da tela
            largura, altura = pyautogui.size() # retorna uma tupla (largura, altura) da tela
            module_logger.info(f"Resolução da tela atual: {largura}x{altura}")

            # Calcular o centro
            centro_x = round(largura / 2)  # round() arredonda para o inteiro mais próximo.
            centro_y = round(altura / 2)

            # Mover o mouse para o centro e clicar
            # pyautogui.moveTo(centro_x, centro_y)
            # pyautogui.click()

            # Clicar nas coordenadas Ex.:(200, 120)
            for _ in range(3):
                self.janela.click_input(coords=(centro_x, centro_y))

            # Digitar um texto diretamente
            self.janela.type_keys(modulo, with_spaces=True, pause=0.05)

            # Pressionar Enter
            self.janela.type_keys("{ENTER}")

    def procurar_obter_janela_principal(self):
        """Conecta a janela principal: Sistema Comercial Nagem.
        
        :returns: A janela conectada.
        :rtype: pywinauto.Application
        """
        module_logger.info("Conectando a janela principal: Sistema Comercial Nagem...")
        try:
            self.app = Application(backend='win32').connect(title_re="Sistema Comercial Nagem.*")
        except:
            self.app = Application(backend='uia').connect(title_re="Sistema Comercial Nagem.*")

        try:
            janela_principal = self.app.window(title_re=".*Sistema Comercial Nagem.*", class_name="TfCONagem0")

            if janela_principal.wait('exists enabled visible ready', timeout=self.default_timeout):
                return janela_principal
        except Exception as erro:
            raise Exception(f"❌  Erro ao obter janela principal: {erro}")

    def acessar_subjanela(self, janela, classe_subjanela: str, titulo_subjanela: Optional[str] = None):
        """Acessa subjanelas dentro de alguma janela principal.
        
        :param janela: instancia da janela conectada
        :type janela: pywinauto.Application

        :param classe_subjanela: Nome da classe da janela
        :type classe_subjanela: str

        :param titulo_subjanela: Título da janela
        :type titulo_subjanela: str

        :returns: A subjanela conectada.
        :rtype: pywinauto.Application
        """

        # obtendo o modulo desejado dentro do MDIclient
        module_logger.info("Procurando subjanela...")
        try:
            if titulo_subjanela:
                subjanela = janela.child_window(
                    title_re=titulo_subjanela,
                    class_name=classe_subjanela
                )
            else:
                subjanela = janela.child_window(class_name=classe_subjanela)
        except Exception as erro:
            raise Exception(f"❌  Erro ao localizar a subjanela: {erro}")
        

        try:
            subjanela.wait("visible", timeout=5)
            subjanela.set_focus()
            module_logger.info("✅  Subjanela encontrada e ativa.")
            return subjanela
        except Exception as erro:
            raise Exception(f"❌  Erro ao visualizar e ativar subjanela: {erro}")

    def procurar_subjanela_mdiclient(self, janela, classe_janela: str, titulo_janela: Optional[str] = None):
        """Obtem o MDIclient dentro da janela principal.
        
        :param janela: instancia da janela conectada
        :type janela: pywinauto.Application

        :param classe_janela: Nome da classe da janela
        :type classe_janela: str

        :param titulo_janela: Título da janela
        :type titulo_janela: str

        :returns: A subjanela MDIclient conectada.
        :rtype: pywinauto.Application
        """
        try:
            mdi = janela.child_window(class_name="MDIClient")
        except Exception as erro:
            raise Exception(f"❌  Erro ao Obter o container MDI: {erro}")


        # obtendo o modulo desejado dentro do MDIclient
        module_logger.info("Procurando janela do módulo...")
        try:
            if titulo_janela:
                janela_modulo = mdi.child_window(
                    title_re=titulo_janela,
                    class_name=classe_janela
                )
            else:
                janela_modulo = mdi.child_window(class_name=classe_janela)
        except Exception as erro:
            raise Exception(f"❌  Erro ao localizar a janela do módulo COREL967: {erro}")
        

        try:
            janela_modulo.wait("visible", timeout=5)
            janela_modulo.set_focus()
            module_logger.info("✅  Janela do módulo encontrada e ativa.")
            return janela_modulo
        except Exception as erro:
            raise Exception(f"❌  Erro ao visualizar e ativar janela: {erro}")

    def clicar_botao(self, janela, titulo_btn: str, classe_btn: str, tipo_btn: Optional[str] = None):
        """Clicando em algum botão pelo titulo(title_re), classe(class_name) e tipo(control_type)"""
        module_logger.info(f"Clicando em {titulo_btn}...")
        try:
            if tipo_btn is not None:
                btn = janela.child_window(title_re=titulo_btn, class_name=classe_btn, control_type=titulo_btn)
            else:
                btn = janela.child_window(title_re=titulo_btn, class_name=classe_btn)
            btn.click_input()
            module_logger.info(f"✅  Botão clicado")
            return True
        except Exception as erro:
            raise Exception(f"❌  Erro ao clicar no botão {titulo_btn}: {erro}")

    def fechar_popup(self, titulo: str, classe: str, timeout = 10):
        """..."""
        try:
            self.app = Application(backend='win32').connect(title_re=".*Sistema Comercial Nagem.*")
        except:
            self.app = Application(backend='uia').connect(title_re=".*Sistema Comercial Nagem.*")

        module_logger.info(f"Verificando popup '{titulo}'...")
        try:
            if self.app.window(title=titulo, class_name=classe).wait('exists enabled visible ready', timeout=timeout):
                module_logger.info(f"Popup '{titulo}' encontrado")

                self.app.window(class_name=classe).close()  # fechando janela
                module_logger.info("✅ Popup fechado")

                return True

        except TimeoutError:
            module_logger.info(f"Popup '{titulo}' não encontrado dentro do tempo limite")
            return False
        except Exception as erro:
            module_logger.info(f"❌  Erro não mapeado ao fechar o popup: {erro}")

    def selecionar_combobox(self, janela, classe_combobox: str, modalidade: str, found_index: Optional[int]=None):
        """
        found_index -> para caso o combobox esteja dentro de um grupo (TGroupBox) e nele tenha mais de um campo (['ComboBox', 'ComboBox0', 'ComboBox1'])
        
        """
        module_logger.info("Selecionando %s no combobox...", modalidade)
        try:
            if found_index:
                combo = janela.child_window(class_name=classe_combobox, found_index=found_index)
            else:
                combo = janela.child_window(class_name=classe_combobox)
            combo.select(modalidade)
        except Exception as erro:
            raise Exception(f"❌  Erro ao selecionar {modalidade} no combobox: {erro}")

    def extrair_relatorio_rpa_faturamento_corel93d(self, data_inicial: str, data_final: str, modalidade: str = "TODOS"):
        """
        Preenche o relatório de faturamento (módulo COREL93D) no CoNagem.

        :param data_inicial: Data inicial no formato DD/MM/AAAA
        :type data_inicial: str
        :param data_final: Data final no formato DD/MM/AAAA
        :type data_final: str
        :param modalidade: Texto exato ou parcial da opção no ComboBox "Modalidade"
        :type modalidade: str
        """
        janela_principal = self.procurar_obter_janela_principal()

        janela_modulo = self.procurar_subjanela_mdiclient(janela_principal,
                                                         classe_janala="TfCOREL93D",
                                                         titulo_janela="Relatório de Faturamento por Filial.*COREL93D")


        module_logger.info("Preenchendo datas...")
        try:
            edits = janela_modulo.children(class_name="TMaskEdit")
            if len(edits) >= 2:
                edits[0].set_text(data_inicial)
                edits[1].set_text(data_final)
            else:
                module_logger.warning("Campos de data não encontrados (TMaskEdit).")
                raise Exception("Campos de data não encontrados (TMaskEdit).")
        except Exception as erro:
            raise Exception(f"❌  Erro no preenchimento das datas: {erro}")


        module_logger.info("Selecionando modalidade: %s...", modalidade)
        try:
            combo = janela_modulo.child_window(class_name="TComboBox")
            combo.select(modalidade)
        except Exception as erro:
            raise Exception(f"❌  Erro ao selecionar a modalidade: {erro}")

        
        time.sleep(0.5)  # Pequeno delay para estabilidade do UI


        self.clicar_botao(janela_modulo,
                           ".*Imprimir.*",
                           "TBitBtn")
        
        # --------------------------------------------------------------------------
        retorno = self.fechar_popup("Atenção", "TMessageForm", 10)
                  
        if retorno:
            janela_modulo.close()  # fechando janela do modulo
            return None
        else:

            janela_principal = self.procurar_obter_janela_principal()

            module_logger.info("Acessando tela do relatório...") # fica na tela principal
            self.clicar_botao(janela_principal,
                            "RPA",
                            "TButton")
            
            # --------------------------------------------------------------------------
            self.fechar_popup("Informação", "TMessageForm")


            module_logger.info("✅ Relatório de Faturamento gerado com sucesso.")

        return True

    def extrair_relatorio_rpa(self, classe_jan_modulo: str, titulo_jan_modulo: str,
                              classe_jan_relatorio: str, titulo_jan_relatorio: str,
                              titulo_btn_rpa_jan_modulo: str = '&RPA', classe_btn_rpa_jan_modulo: str= 'TBitBtn',
                              titulo_btn_rpa_jan_relatorio: str = 'RPA', classe_btn_rpa_jan_relatorio: str = 'TButton'):
        """
        Extrai relatórios de módulos dentro do conagem

        :param botclasse_jan_moduloao_ctrl: Nome da classe da janela do módulo.
        :type classe_jan_modulo: str

        :param titulo_jan_modulo: Título da janela do módulo.
        :type titulo_jan_modulo: str

        :param classe_jan_relatorio: Nome da classe da janela do relatório.
        :type classe_jan_relatorio: str

        :param titulo_jan_relatorio: Título da janela do relatório.
        :type titulo_jan_relatorio: str

        :param titulo_btn_rpa_jan_modulo: Título do botão RPA na janela do módulo.
        :type titulo_btn_rpa_jan_modulo: str

        :param classe_btn_rpa_jan_modulo: Nome da classe do botão RPA na janela do módulo.
        :type classe_btn_rpa_jan_modulo: str

        :param titulo_btn_rpa_jan_relatorio: Título do botão RPA na janela do relatório.
        :type titulo_btn_rpa_jan_relatorio: str

        :param classe_btn_rpa_jan_relatorio: Nome da classe do botão RPA na janela do relatório.
        :type classe_btn_rpa_jan_relatorio: str

        :returns: True caso o relatorio seja extraido, False caso contrario
        :rtype: bool, None 
        """
        janela_principal = self.procurar_obter_janela_principal()

        janela_modulo = self.procurar_subjanela_mdiclient(janela_principal,
                                                         classe_janala=classe_jan_modulo,
                                                         titulo_janela=titulo_jan_modulo)

        module_logger.info(f"Clicando em {titulo_btn_rpa_jan_modulo}... (Tela do modulo)")
        self.clicar_botao(janela_modulo,
                        titulo_btn_rpa_jan_modulo,
                        classe_btn_rpa_jan_modulo)

        retorno_info = self.fechar_popup("Informação", "TMessageForm")
        retorno_sac = self.fechar_popup("SAC - Sistema de Automação Comercial [ SAP RETAIL ]", "TMessageForm")

        if retorno_info or retorno_sac:
            janela_modulo.close()  # fechando janela do modulo
            return None
        else:

            janela_principal = self.procurar_obter_janela_principal()

            janela_modulo2 = self.procurar_subjanela_mdiclient(janela_principal,
                                                            classe_janala=classe_jan_relatorio,
                                                            titulo_janela=titulo_jan_relatorio)

            module_logger.info("Acessando tela do relatório...") # fica na tela principal
            self.clicar_botao(janela_modulo2,
                            titulo_btn_rpa_jan_relatorio,
                            classe_btn_rpa_jan_relatorio)
            
            self.fechar_popup("Informação", "TMessageForm")
            janela_modulo.close()  # fechando janela do modulo

            return True

    def fechar_aplicacao(self) -> None:
        """
        Fecha progrma. Não força fechamento do app a menos que queira.
        """
        self.app.kill()
        self.janela = None
        self.app = None
        self.programa_conectado = False
        module_logger.info("✅  Processo conagem encerrado")

    # def conectar_janela(self, titulo_janela: str, aguardar_janela: bool = True):
    #     """..."""
    #     # self.app = Application(backend=self.backend).connect(title_re=f".*{titulo_janela}.*")
        
    #     try:
    #         self.janela = self.app.window(title_re=f".*{titulo_janela}.*")
    #     except Exception as erro:
    #         raise Exception(f"❌  Erro ao conectar a janela {titulo_janela}: {erro}")

    #     if aguardar_janela:
    #         try:
    #             module_logger.info("Aguardando janela ficar visível...")
    #             self.janela.wait('exists enabled visible ready', timeout=self.default_timeout)
    #         except Exception as erro:
    #             module_logger.info(f"❌ Janela não encontrada. Erro: {erro}")
    #             raise Exception(f"❌ Janela não encontrada. Erro: {erro}")

    #     return self.obter_controles_janela()
