from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import base64

from rpanagem import manipula_diretorios_arquivos
import logging
logger = logging.getLogger(__name__)
log = manipula_diretorios_arquivos.Arquivos()
module_logger = log.criar_logger_diario("./log", nome_arquivo_log="manipula_navegador.log", logger=logger)


class Navegador:
    """
    Inicializa a automação de login no Sitef.
    Apenas define atributos e estado inicial.
    """
    def __init__(self, headless: bool = True, dir_log_rpa: str = "C:/RPA/log"):
        """Iniciando variáveis.

        :param headless: True para executar o navegador em um modo sem interface gráfica, False para mostrar interface.
        :type headless: bool
        :param dir_log_rpa: Caminho do diretório para gravar arquivos de log.
        :type dir_log_rpa: str
        """
        module_logger.info("____________INICIANDO ROBO______________")
        self.headless = headless
        self.dir_log_rpa = dir_log_rpa + '/printscreen.png'

        self.driver = None
        self.wait = None

    def iniciar_driver_chrome(self, dir_download_arquivos: str = "C:"):
        """Inicia o ChromeDriver com as opções definidas.
        
        :param dir_download_arquivos: Caminho do diretório para gravar arquivos de download.
        :type dir_download_arquivos: str
        """
        self.dir_download_arquivos = dir_download_arquivos

        try:
            module_logger.info("Iniciando o ChromeDriver...")
            chrome_options = Options()

            # chrome_options.add_argument("--headless")  # descomente se quiser sem interface
            if self.headless:
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--window-size=1920,1080")  # resolução alta

            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--start-maximized")  # abrir janela cheia
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Desliga o logging do ChromeDriver
            chrome_options.add_argument("--log-level=4")  # 0=ALL, 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR, 5=FATAL

            # Desativar o visualizador de PDF do Chrome e baixar direto
            prefs = {
                "download.default_directory": self.dir_download_arquivos,  # pasta onde vai salvar
                "plugins.always_open_pdf_externally": True,  # Desativa o PDF Viewer do Chrome → qualquer PDF é baixado automaticamente.
                "download.prompt_for_download": False,  # não perguntar onde salvar
                "directory_upgrade": True,
                "safebrowsing.enabled": True,
                "profile.default_content_settings.popups": 0
            }
            chrome_options.add_experimental_option("prefs", prefs)

            service = Service()  # se precisar, coloque o caminho do chromedriver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)

            return self.driver
        except Exception as e:
            module_logger.error(f"❌ Falha ao iniciar o driver: {e}")
            module_logger.error(f"Salvando printscreen em {self.dir_log_rpa}")
            self.driver.save_screenshot(self.dir_log_rpa)
            self.finalizar()

    def fazer_login(self, url_login: str, usuario: str, senha: str, id_campo_login: str, id_campo_senha: str, id_campo_btn: str):
        """Realiza o login no portal Sitef.
        
        :param url_login: ulr do site que se deseja acessar.
        :type url_login: str

        :param usuario: Usuario para autenticação.
        :type usuario: str

        :param senha: Senha para autenticação.
        :type senha: str

        :param id_campo_login: id para acessar o campo usuario.
        :type id_campo_login: str

        :param id_campo_senha: id para acessar o campo senha.
        :type id_campo_senha: str

        :param id_campo_btn: id para acessar o botão de logar.
        :type id_campo_btn: str
        """

        module_logger.info("Acessando a página de login...")
        self.driver.get(url_login)

        try:
            # Aguarda o campo de usuário aparecer
            campo_usuario = self.wait.until(EC.presence_of_element_located((By.ID, id_campo_login)))
            campo_usuario.clear()
            campo_usuario.send_keys(usuario)

            # Aguarda o campo de senha
            campo_senha = self.wait.until(EC.presence_of_element_located((By.ID, id_campo_senha)))
            campo_senha.clear()
            campo_senha.send_keys(senha)

            # enter na pagina
            # campo_senha.send_keys(Keys.RETURN)

            self.wait.until(EC.element_to_be_clickable((By.ID, id_campo_btn))).click()

            final_url = self.driver.current_url
            module_logger.info(f"✅ Login concluído. URL final: {final_url}")

        except Exception as e:
            # print(f"[ERRO] Falha no login: {e}")
            module_logger.error(f"❌ Falha no login: {e}")
            module_logger.error(f"Salvando printscreen em {self.dir_log_rpa}")
            self.driver.save_screenshot(self.dir_log_rpa)
            self.finalizar()

    def gerar_pdf_pagina(self, caminho_arquivo):
        """
        Gera um PDF real da página atual usando o comando CDP `Page.printToPDF`.

        :param caminho_arquivo: Caminho completo onde o PDF será salvo (incluindo o nome do arquivo com extensão).
        :ptype caminho_arquivo: str
        """
        try:
            # Usa o Chrome DevTools Protocol para gerar o PDF
            pdf_data = self.driver.execute_cdp_cmd("Page.printToPDF", {
                "printBackground": True,  # Mantém imagens e estilos CSS aplicados como background
                "landscape": False,  # Define a orientação da página. False → Retrato (portrait) True → Paisagem (landscape)
                "paperWidth": 8.27,   # Largura do PDF em polegadas. 8.27 é exatamente a largura de uma folha A4.
                "paperHeight": 11.69, # Altura do PDF em polegadas. 11.69 é tamanho exato de uma folha A4.
                "marginTop": 0.4,  # (0,4 polegadas = ~1 cm)
                "marginBottom": 0.4,
                "marginLeft": 0.4,
                "marginRight": 0.4,
            })

            # Valida retorno
            if not pdf_data or "data" not in pdf_data:
                module_logger.info("❌ Erro: O comando printToPDF não retornou dados.")
                print("❌ Erro: O comando printToPDF não retornou dados.")
                return False

            # Decodifica hexadecimal
            # pdf_bytes = bytes.fromhex(pdf['data'])

            # Decodifica Base64
            pdf_bytes = base64.b64decode(pdf_data['data'])

            # Salva o PDF
            with open(caminho_arquivo, "wb") as f:
                f.write(pdf_bytes)

            module_logger.info(f"✅ PDF gerado com sucesso em: {caminho_arquivo}")
            print(f"✅ PDF gerado com sucesso em: {caminho_arquivo}")
            return True
        except Exception as erro:
            module_logger.info(f"❌ Erro não mapeado ao imprimir a tela para pdf: {erro}")
            print(f"❌ Erro não mapeado ao imprimir a tela para pdf: {erro}")
            module_logger.error(f"Salvando printscreen em {self.dir_log_rpa}")
            self.driver.save_screenshot(self.dir_log_rpa)
            return False

    def localizar_elemento(self, elemento: str, tipo_elemento: str = 'id'):
        """..."""
        self.verificar_tipo_elemento(tipo_elemento)

        try:
            elemento_localizado = self.wait.until(EC.presence_of_element_located((self.by, elemento)))
        except Exception as erro:
            print(f"⚠️  Elemento '{elemento}' não foi encontrado no documento principal: {erro}")
            elemento_localizado = self.procurar_elemento_iframe(elemento, tipo_elemento)
        
        if elemento_localizado:
            module_logger.error(f"✅ Elemento {elemento} não localizado")
            print(f"✅  Elemento {elemento} localizado")
            return True
        else:
            module_logger.error(f"❌ Elemento {elemento} não localizado")
            print(f"❌  Elemento {elemento} não localizado")
            return False

    def buscar_texto_no_dom(self, texto_antecessor: str, indice_texto_desejado: int):
        """
        Busca um texto específico dentro do DOM atual usando page_source.

        :param texto_antecessor: Texto antecessor do texto desejado a ser procurado dentro do DOM.
        :ptype texto_antecessor: str
        :param indice_texto_desejado: Quantidade de caracter do texto desejado apos o texto antecessor (vai servir como indice).
        :ptype indice_texto_desejado: int
    
        :return: dict contendo:
            - existe (bool): True se o texto foi encontrado, False caso contrário.
            - primeiro_indice (int | None): Posição inicial da primeira ocorrência.
            - ultimo_indice (int | None): Posição inicial da última ocorrência.
            - erro (str | None): Mensagem de erro caso ocorra alguma exceção.
        """

        resultado = {
            "existe": False,
            "primeiro_indice": None,
            "ultimo_indice": None,
            "erro": None
        }

        try:
            if not texto_antecessor or not isinstance(texto_antecessor, str):
                # logger
                raise ValueError("O parâmetro 'texto_antecessor' deve ser uma string não vazia.")

            # Obtém o DOM da página atual
            try:
                # html = self.driver.page_source
                body = self.driver.find_element(By.TAG_NAME, "body")
                texto_visivel = body.text
            except Exception as erro:
                # logger
                raise RuntimeError(f"❌ Não foi possível obter o DOM: {erro}")

            # Busca os índices
            primeiro_indice = texto_visivel.find(texto_antecessor)
            ultimo_indice = primeiro_indice + len(texto_antecessor)

            if primeiro_indice != -1:
                resultado["existe"] = True
                resultado["primeiro_indice"] = primeiro_indice
                resultado["ultimo_indice"] = ultimo_indice
                resultado["texto"] = texto_visivel[ultimo_indice:ultimo_indice+indice_texto_desejado]

            print(f"ℹ️  Resultado texto DOM: {resultado}")
            return resultado

        except Exception as e:
            resultado["erro"] = str(e)
            return resultado

    def clicar_elemento(self, elemento: str, tipo_elemento: str = 'id'):
        """..."""
        self.verificar_tipo_elemento(tipo_elemento)

        try:
            elemento_clicavel = self.wait.until(EC.presence_of_element_located((self.by, elemento)))
        except Exception as erro:
            print(f"⚠️  Elemento '{elemento}' não foi encontrado no documento principal: {erro}")
            elemento_clicavel = self.procurar_elemento_iframe(elemento, tipo_elemento)

        if elemento_clicavel:
            try:
                # elemento_clicavel = self.wait.until(EC.presence_of_element_located((self.by, elemento)))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", elemento_clicavel)
                self.driver.execute_script("arguments[0].click();", elemento_clicavel)
                print(f"✅  Elemento {elemento} clicado")
            except Exception as e:
                module_logger.error(f"❌ Falha ao clicar no elemento {elemento} ERRO: {e}")
                module_logger.error(f"Salvando printscreen em {self.dir_log_rpa}")
                self.driver.save_screenshot(self.dir_log_rpa)
                self.finalizar()
                raise Exception(f"❌ Falha ao clicar no elemento: {elemento} - ERRO: {e}")

    def digitar_elemento(self, elemento: str, valor, tipo_elemento: str = 'id'):
        """..."""
        self.verificar_tipo_elemento(tipo_elemento)

        try:
            elemento_input = self.wait.until(EC.element_to_be_clickable((self.by, elemento)))
        except Exception as erro:
            print(f"⚠️  Elemento '{elemento}' não foi encontrado no documento principal: {erro}")
            elemento_input = self.procurar_elemento_iframe(elemento, tipo_elemento)

        if elemento_input:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", elemento_input)
                elemento_input.clear()
                elemento_input.send_keys(valor)
                # self.driver.execute_script(f"document.getElementById('{id_elemento}').value = '{valor}';")

                print(f"✅  Valor '{valor}' inserido no elemento '{elemento}'")
            except Exception as erro:
                module_logger.error(f"❌  Falha ao digitar no elemento: {elemento}: {erro}")
                module_logger.error(f"Salvando printscreen em {self.dir_log_rpa}")
                self.driver.save_screenshot(self.dir_log_rpa)
                self.finalizar()
                raise Exception(f"❌  Falha ao digitar no elemento: {elemento}: {erro}")

    def selecionar_tag_select(self, elemento: str, valor, tipo_elemento: str = 'id'):
        """..."""
        self.verificar_tipo_elemento(tipo_elemento)

        try:
            select_element = self.wait.until(EC.element_to_be_clickable((self.by, elemento)))
        except Exception as erro:
            print(f"⚠️  Elemento '{elemento}' não foi encontrado no documento principal: {erro}")
            select_element = self.procurar_elemento_iframe(elemento, tipo_elemento)
        
        if select_element:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", select_element)
                select = Select(select_element)
                select.select_by_value(valor)
            except Exception as erro:
                module_logger.error(f"Salvando printscreen em {self.dir_log_rpa}")
                self.driver.save_screenshot(self.dir_log_rpa)
                module_logger.error(f"❌  Falha ao selecionar o elemento: {elemento}: {erro}")
                self.finalizar()
                raise Exception(f"❌  Falha ao selecionar o elemento: {elemento}: {erro}")

    def selecionar_checkbox(self, elemento: str, tipo_elemento: str = 'id'):
        """..."""
        self.verificar_tipo_elemento(tipo_elemento)

        try:
            checkbox = self.wait.until(EC.element_to_be_clickable((self.by, elemento)))
        except Exception as erro:
            print(f"⚠️  Elemento '{elemento}' não foi encontrado no documento principal: {erro}")
            checkbox = self.procurar_elemento_iframe(elemento, tipo_elemento)
        
        if checkbox:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                checkbox.click()
                # clicar apenas se ainda não marcado
                if not checkbox.is_selected():
                    checkbox.click()

                    # OBS.: ELEMENTOS COM PONTOS NÃO FUNCIONAM COM By.CSS_SELECTOR, "#chk_5.102" PORQUE ELE INTERPRETA .102 COMO CLASSE.

            except Exception as erro:
                module_logger.error(f"Salvando printscreen em {self.dir_log_rpa}")
                self.driver.save_screenshot(self.dir_log_rpa)
                module_logger.error(f"❌  Falha ao selecionar o elemento: {elemento}: {erro}")
                self.finalizar()
                raise Exception(f"❌  Falha ao selecionar o elemento: {elemento}: {erro}")

    def voltar_contexto_principal(self):
        """voltar para o contexto/documento/tela principal."""
        self.driver.switch_to.default_content()

    def verificar_tipo_elemento(self, tipo_elemento: str = 'id'):
        """..."""
        if tipo_elemento == 'classe':
            self.by = By.CLASS_NAME
        elif tipo_elemento == 'xpath':
            self.by = By.XPATH
        elif tipo_elemento == 'name':
            self.by = By.NAME
        elif tipo_elemento == 'css':
            self.by = By.CSS_SELECTOR
        else:
            self.by = By.ID

    def procurar_elemento_iframe(self, elemento, tipo_elemento: str = 'id'):
        """..."""
        self.verificar_tipo_elemento(tipo_elemento)

        # voltar para o contexto/documento principal:
        self.driver.switch_to.default_content()

        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        print(f"ℹ️  Total iframes encontrados: {len(iframes)}")

        if iframes:
            for i, iframe in enumerate(iframes):
                # title_iframe = iframe.get_attribute('title')
                # name_iframe = iframe.get_attribute('name')
                # id_iframe = iframe.get_attribute('id')
                # print(f"ℹ️  IFRAME {i} =>> title={iframe.get_attribute('title')} | name={iframe.get_attribute('name')} | id={iframe.get_attribute('id')}")
                print(f"ℹ️  IFRAME {i} =>> {iframe}")

                # voltar para o contexto/documento principal:
                self.driver.switch_to.default_content()

                # trocar o contexto
                # self.driver.switch_to.frame(id_iframe)
                # ou, se precisar usar índice:
                self.driver.switch_to.frame(iframes[i])

                print('Verificando elemento visivel no iframe...')
                # Para confirmar se o campo está visível após o switch_to.frame:
                try:
                    elemento_input = self.driver.find_element(self.by, elemento)
                    print('ℹ️  HTML do input: ', elemento_input.get_attribute("outerHTML"))  # Se imprimir o HTML do input corretamente, você está no contexto certo.
                    break
                except:
                    elemento_input = None

            if elemento_input is None:
                print(f"❌  Elemento '{elemento}' não foi encontrado em nenhum dos iframes")
                self.finalizar()
                raise Exception(f"❌ Elemento '{elemento}' não foi encontrado em nenhum dos iframes")
            return elemento_input
        else:
            self.finalizar()
            raise Exception('❌ Nenhum iframe encontrado na página.')

    def obter_nova_janela_navegador(self):
        """Alterar o controle para a nova janela do navegador."""

        # Guardar o handle, o titulo e a url da janela antes de abrir a nova
        self.original_handle = self.driver.current_window_handle
        self.original_title = self.driver.title
        self.original_url = self.driver.current_url

        # O Selenium guarda todas as janelas abertas em: driver.window_handles (Isso retorna uma lista com os "IDs" de cada janela aberta.)
        print(f'ℹ️  JANELAS ENCONTRADAS: {self.driver.window_handles}')
        # try:
        #     for janela in self.driver.window_handles:
        #         self.driver.switch_to.window(janela)
        #         # if "Algum título" in self.driver.title:
        #         #     break
        #         print(f'► Título: {self.driver.title} | ► URL: {self.driver.current_url}')
        # except:
        #     pass
            
        try:
            # obter nova janela
            nova_janela = self.driver.window_handles[-1]  # Geralmente, a nova é a última:
            self.driver.switch_to.window(nova_janela)

            # ou
            # for janela in self.driver.window_handles:
            #     if janela != self.janela_principal:
            #         self.driver.switch_to.window(janela)
            #         break
            print("ℹ️  Mudou para a nova janela:", self.driver.current_url)
        except Exception as erro:
            module_logger.error(f"Salvando printscreen em {self.dir_log_rpa}")
            self.driver.save_screenshot(self.dir_log_rpa)
            module_logger.error(f"❌ Falha ao obter a nova janela: {erros}")
            print(f"❌ Falha ao obter a nova janela: {erro}")
            self.finalizar()

    def voltar_janela_principal(self):
        """Volta prar o controle da janela principal."""
        print(f'ℹ️  JANELAS ENCONTRADAS: {self.driver.window_handles}')

        try:
            # for janela in self.driver.window_handles:
            self.driver.switch_to.window(self.driver.window_handles[0])
                # if (self.driver.current_window_handle == self.original_handle or
                #     self.driver.title == self.original_title or
                #     self.driver.current_url == self.original_url):
                #     return True
        except Exception as erro:
            module_logger.error(f"❌ Falha ao obter a janela atual: {erro}")
            print(f"❌ Falha ao voltar para a janela principal: {erro}")
            self.finalizar()

    def finalizar(self):
        """Fecha o navegador."""
        if self.driver:
            self.driver.quit()
