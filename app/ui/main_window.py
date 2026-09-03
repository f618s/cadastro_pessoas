"""Janela principal da aplicação.

Esta classe tem uma responsabilidade específica: orquestrar os widgets
(formulários e tabela), o serviço de banco de dados e o worker de
consulta de CEP. A construção visual de cada bloco do formulário fica
nas classes em app/ui/widgets - aqui só existe a "cola" entre eles.
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.exceptions import BancoDadosError
from app.models import Pessoa
from app.validators import (
    somente_numeros,
    validar_celular,
    validar_cep,
    validar_documento,
    validar_email,
)
from app.workers.cep_worker import CepWorker
from app.ui.styles import ESTILO_APLICACAO
from app.ui.widgets.address_form import AddressForm
from app.ui.widgets.person_table import PersonTable
from app.ui.widgets.personal_data_form import PersonalDataForm

logger = logging.getLogger(__name__)

MENSAGENS_ERRO_CEP = {
    "invalido": "CEP inválido",
    "nao_encontrado": "CEP não encontrado",
    "conexao": "Erro de conexão",
    "resposta_invalida": "Resposta inesperada do serviço",
    "inesperado": "Erro inesperado",
}


class CadastroWindow(QMainWindow):
    def __init__(self, database):
        super().__init__()

        self.db = database
        self._editando_id: int | None = None
        self._cep_worker: CepWorker | None = None

        self.setWindowTitle("Sistema de Cadastro de Pessoas")
        self.setMinimumSize(980, 760)

        self._montar_menu()
        self._montar_interface()
        self.setStyleSheet(ESTILO_APLICACAO)

        self.statusBar().showMessage("Pronto.")
        self._carregar_tabela()

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------

    def _montar_menu(self):
        menu_arquivo = self.menuBar().addMenu("&Arquivo")

        acao_novo = menu_arquivo.addAction("Novo cadastro")
        acao_novo.setShortcut("Ctrl+N")
        acao_novo.triggered.connect(self._novo_cadastro)

        menu_arquivo.addSeparator()

        acao_sair = menu_arquivo.addAction("Sair")
        acao_sair.setShortcut("Ctrl+Q")
        acao_sair.triggered.connect(self.close)

        menu_ajuda = self.menuBar().addMenu("A&juda")
        acao_sobre = menu_ajuda.addAction("Sobre")
        acao_sobre.triggered.connect(self._mostrar_sobre)

    def _montar_interface(self):
        central = QWidget()
        central.setObjectName("areaCentral")
        layout_principal = QVBoxLayout(central)
        layout_principal.setContentsMargins(20, 16, 20, 16)
        layout_principal.setSpacing(10)

        titulo = QLabel("Cadastro de Pessoa")
        titulo.setObjectName("titulo")

        self.subtitulo = QLabel("Preencha os dados abaixo para realizar o cadastro.")
        self.subtitulo.setObjectName("subtitulo")

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(self.subtitulo)

        self.form_pessoais = PersonalDataForm()
        self.form_endereco = AddressForm()
        self.form_endereco.consulta_solicitada.connect(self._consultar_endereco)

        layout_principal.addWidget(self.form_pessoais)
        layout_principal.addWidget(self.form_endereco)

        botoes = QHBoxLayout()
        self.btn_cancelar_edicao = QPushButton("Cancelar edição")
        self.btn_cancelar_edicao.setObjectName("botaoSecundario")
        self.btn_cancelar_edicao.clicked.connect(self._novo_cadastro)
        self.btn_cancelar_edicao.setVisible(False)

        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.setObjectName("botaoSecundario")
        self.btn_limpar.clicked.connect(self._limpar_com_confirmacao)

        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.clicked.connect(self._salvar)

        botoes.addStretch()
        botoes.addWidget(self.btn_cancelar_edicao)
        botoes.addWidget(self.btn_limpar)
        botoes.addWidget(self.btn_cadastrar)
        layout_principal.addLayout(botoes)

        self.tabela_pessoas = PersonTable()
        self.tabela_pessoas.editar_solicitado.connect(self._editar_pessoa)
        self.tabela_pessoas.excluir_solicitado.connect(self._excluir_pessoa)
        self.tabela_pessoas.pesquisa_alterada.connect(self._carregar_tabela)
        self.tabela_pessoas.atualizar_solicitado.connect(lambda: self._carregar_tabela())
        layout_principal.addWidget(self.tabela_pessoas)

        self.setCentralWidget(central)

    def _mostrar_sobre(self):
        QMessageBox.information(
            self,
            "Sobre",
            "Sistema de Cadastro de Pessoas\n"
            "Desenvolvido em Python com PySide6.\n\n"
            "Consulta de endereço via API pública ViaCEP.",
        )

    # ------------------------------------------------------------------
    # Validação
    # ------------------------------------------------------------------

    def _validar_formulario(self, dados: dict):
        """Retorna (lista_de_mensagens, conjunto_de_campos_invalidos)."""
        erros = []
        campos_invalidos = set()

        nome = dados["nome"]
        documento = somente_numeros(dados["documento"])
        email = dados["email"]
        celular = somente_numeros(dados["celular"])
        cep = somente_numeros(dados["cep"])

        if not nome:
            erros.append("Informe o nome completo.")
            campos_invalidos.add("nome")

        if not documento:
            erros.append("Informe o CPF/CNPJ.")
            campos_invalidos.add("documento")
        elif not validar_documento(dados["tipo_documento"], documento):
            erros.append(f"O {dados['tipo_documento']} informado é inválido.")
            campos_invalidos.add("documento")

        if not email:
            erros.append("Informe o e-mail.")
            campos_invalidos.add("email")
        elif not validar_email(email):
            erros.append("O e-mail possui formato inválido. Exemplo: usuario@email.com.")
            campos_invalidos.add("email")

        if not celular:
            erros.append("Informe o celular.")
            campos_invalidos.add("celular")
        elif not validar_celular(celular):
            erros.append("O celular deve possuir DDD e 9 dígitos. Exemplo: (11) 99999-9999.")
            campos_invalidos.add("celular")

        if not cep:
            erros.append("Informe o CEP.")
            campos_invalidos.add("cep")
        elif not validar_cep(cep):
            erros.append("O CEP deve possuir 8 dígitos. Exemplo: 01001-000.")
            campos_invalidos.add("cep")

        if not dados["logradouro"]:
            erros.append("Informe o logradouro.")
            campos_invalidos.add("logradouro")

        if not dados["numero"]:
            erros.append("Informe o número.")
            campos_invalidos.add("numero")

        if not dados["bairro"]:
            erros.append("Informe o bairro.")
            campos_invalidos.add("bairro")

        if not dados["cidade"]:
            erros.append("Informe a cidade.")
            campos_invalidos.add("cidade")

        if not dados["estado"]:
            erros.append("Selecione o estado.")
            campos_invalidos.add("estado")

        return erros, campos_invalidos

    def _coletar_dados(self) -> dict:
        dados = {}
        dados.update(self.form_pessoais.obter_dados())
        dados.update(self.form_endereco.obter_dados())
        return dados

    # ------------------------------------------------------------------
    # Consulta de CEP (assíncrona)
    # ------------------------------------------------------------------

    def _consultar_endereco(self, cep: str):
        if self._cep_worker is not None and self._cep_worker.isRunning():
            self.statusBar().showMessage("Já existe uma consulta de CEP em andamento...", 4000)
            return

        if not validar_cep(somente_numeros(cep)):
            self.form_endereco.finalizar_consulta_visual(
                "Informe um CEP válido com 8 dígitos. Exemplo: 01001-000."
            )
            return

        self.form_endereco.iniciar_consulta_visual()
        self.statusBar().showMessage("Consultando endereço...")

        self._cep_worker = CepWorker(cep, parent=self)
        self._cep_worker.sucesso.connect(self._ao_consultar_endereco_sucesso)
        self._cep_worker.falha.connect(self._ao_consultar_endereco_falha)
        self._cep_worker.finished.connect(self._cep_worker.deleteLater)
        self._cep_worker.start()

    def _ao_consultar_endereco_sucesso(self, endereco: dict):
        self.form_endereco.preencher_endereco(endereco)
        self.form_endereco.finalizar_consulta_visual(mensagem_erro=None)
        self.statusBar().showMessage("Endereço localizado com sucesso.", 4000)

    def _ao_consultar_endereco_falha(self, categoria: str, mensagem: str):
        self.form_endereco.finalizar_consulta_visual(mensagem_erro=mensagem)
        titulo = MENSAGENS_ERRO_CEP.get(categoria, "Erro")

        if categoria in ("conexao", "resposta_invalida", "inesperado"):
            QMessageBox.critical(self, titulo, mensagem)
        else:
            QMessageBox.warning(self, titulo, mensagem)

        self.statusBar().showMessage("Não foi possível consultar o CEP.", 4000)

    # ------------------------------------------------------------------
    # Cadastrar / atualizar
    # ------------------------------------------------------------------

    def _salvar(self):
        dados = self._coletar_dados()
        erros, campos_invalidos = self._validar_formulario(dados)

        self.form_pessoais.destacar_campos_invalidos(campos_invalidos)
        self.form_endereco.destacar_campos_invalidos(campos_invalidos)

        if erros:
            QMessageBox.warning(
                self,
                "Corrija os dados",
                "Foram encontrados os seguintes problemas:\n\n"
                + "\n".join(f"• {erro}" for erro in erros),
            )
            self.statusBar().showMessage("Corrija os campos destacados em vermelho.", 5000)
            return

        pessoa = Pessoa(
            id=self._editando_id,
            tipo_documento=dados["tipo_documento"],
            documento=somente_numeros(dados["documento"]),
            nome=dados["nome"],
            email=dados["email"],
            celular=somente_numeros(dados["celular"]),
            cep=somente_numeros(dados["cep"]),
            logradouro=dados["logradouro"],
            numero=dados["numero"],
            complemento=dados["complemento"],
            bairro=dados["bairro"],
            cidade=dados["cidade"],
            estado=dados["estado"],
        )

        self.btn_cadastrar.setEnabled(False)
        try:
            if self._editando_id is None:
                self.db.inserir(pessoa)
                mensagem = "Pessoa cadastrada com sucesso!"
            else:
                self.db.atualizar(pessoa)
                mensagem = "Cadastro atualizado com sucesso!"

            QMessageBox.information(self, "Sucesso", mensagem)
            self._novo_cadastro()
            self._carregar_tabela()

        except BancoDadosError as erro:
            QMessageBox.critical(self, "Erro ao salvar", str(erro))
            self.statusBar().showMessage("Não foi possível salvar o cadastro.", 5000)
        except Exception as erro:  # última linha de defesa
            logger.exception("Erro inesperado ao salvar cadastro")
            QMessageBox.critical(
                self,
                "Erro inesperado",
                "Ocorreu um erro inesperado ao salvar o cadastro.\n"
                f"Detalhes técnicos: {erro}",
            )
        finally:
            self.btn_cadastrar.setEnabled(True)

    # ------------------------------------------------------------------
    # Edição / limpeza
    # ------------------------------------------------------------------

    def _editar_pessoa(self, pessoa_id: int):
        try:
            pessoa = self.db.buscar_por_id(pessoa_id)
        except BancoDadosError as erro:
            QMessageBox.critical(self, "Erro", str(erro))
            return

        if pessoa is None:
            QMessageBox.warning(
                self,
                "Cadastro não encontrado",
                "Este cadastro não existe mais (pode ter sido excluído).",
            )
            self._carregar_tabela()
            return

        self.form_pessoais.preencher(pessoa)
        self.form_endereco.preencher(pessoa)
        self._editando_id = pessoa.id

        self.subtitulo.setText(f"Editando o cadastro de {pessoa.nome}.")
        self.btn_cadastrar.setText("Salvar alterações")
        self.btn_cancelar_edicao.setVisible(True)
        self.statusBar().showMessage("Editando cadastro existente.", 4000)

    def _novo_cadastro(self):
        self.form_pessoais.limpar()
        self.form_endereco.limpar()
        self._editando_id = None
        self.subtitulo.setText("Preencha os dados abaixo para realizar o cadastro.")
        self.btn_cadastrar.setText("Cadastrar")
        self.btn_cancelar_edicao.setVisible(False)
        self.form_pessoais.focar_nome()

    def _formulario_possui_dados(self) -> bool:
        return self.form_pessoais.possui_dados_preenchidos() or self.form_endereco.possui_dados_preenchidos()

    def _limpar_com_confirmacao(self):
        if self._formulario_possui_dados():
            resposta = QMessageBox.question(
                self,
                "Limpar formulário",
                "Isso irá apagar os dados preenchidos no formulário. Deseja continuar?",
            )
            if resposta != QMessageBox.StandardButton.Yes:
                return

        self._novo_cadastro()
        self.statusBar().showMessage("Formulário limpo.", 3000)

    # ------------------------------------------------------------------
    # Tabela / exclusão
    # ------------------------------------------------------------------

    def _carregar_tabela(self, termo_pesquisa: str = ""):
        try:
            registros = self.db.listar(termo_pesquisa.strip() if termo_pesquisa else "")
            self.tabela_pessoas.carregar(registros)
        except BancoDadosError as erro:
            QMessageBox.critical(self, "Erro ao carregar cadastros", str(erro))

    def _excluir_pessoa(self, pessoa_id: int):
        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Deseja realmente excluir este cadastro? Esta ação não pode ser desfeita.",
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self.db.excluir(pessoa_id)
            if self._editando_id == pessoa_id:
                self._novo_cadastro()
            self._carregar_tabela()
            self.statusBar().showMessage("Cadastro excluído com sucesso.", 4000)
        except BancoDadosError as erro:
            QMessageBox.critical(self, "Erro ao excluir", str(erro))

    # ------------------------------------------------------------------
    # Encerramento seguro
    # ------------------------------------------------------------------

    def closeEvent(self, event):
        if self._cep_worker is not None and self._cep_worker.isRunning():
            self._cep_worker.terminate()
            self._cep_worker.wait(2000)
        event.accept()
