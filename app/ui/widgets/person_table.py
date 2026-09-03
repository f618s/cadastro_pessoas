"""Widget da lista de cadastros realizados (tabela + pesquisa + ações)."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

COLUNAS = ["ID", "Nome", "Documento", "E-mail", "Celular", "Cidade", "Estado"]


class PersonTable(QGroupBox):
    editar_solicitado = Signal(int)
    excluir_solicitado = Signal(int)
    pesquisa_alterada = Signal(str)
    atualizar_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__("Cadastros realizados", parent)
        self._montar_layout()

    def _montar_layout(self):
        layout = QVBoxLayout(self)

        barra_topo = QHBoxLayout()
        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText("Pesquisar por nome, documento ou e-mail...")
        self.pesquisa.textChanged.connect(self.pesquisa_alterada.emit)

        self.btn_atualizar = QPushButton("Atualizar lista")
        self.btn_atualizar.setObjectName("botaoSecundario")
        self.btn_atualizar.clicked.connect(self.atualizar_solicitado.emit)

        barra_topo.addWidget(self.pesquisa)
        barra_topo.addWidget(self.btn_atualizar)
        layout.addLayout(barra_topo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(len(COLUNAS))
        self.tabela.setHorizontalHeaderLabels(COLUNAS)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setColumnHidden(0, True)  # ID fica oculto, mas acessível
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela.doubleClicked.connect(self._ao_dar_duplo_clique)

        layout.addWidget(self.tabela)

        self.dica = QLabel("Dica: dê um duplo clique em um cadastro para editá-lo.")
        self.dica.setObjectName("mensagemErroCampo")
        self.dica.setStyleSheet("color: #5b6b7b;")
        layout.addWidget(self.dica)

        botoes = QHBoxLayout()
        self.btn_editar = QPushButton("Editar selecionado")
        self.btn_editar.setObjectName("botaoSecundario")
        self.btn_editar.clicked.connect(self._ao_clicar_editar)

        self.btn_excluir = QPushButton("Excluir selecionado")
        self.btn_excluir.setObjectName("botaoPerigo")
        self.btn_excluir.clicked.connect(self._ao_clicar_excluir)

        botoes.addStretch()
        botoes.addWidget(self.btn_editar)
        botoes.addWidget(self.btn_excluir)
        layout.addLayout(botoes)

    # ------------------------------------------------------------------
    # Eventos internos
    # ------------------------------------------------------------------

    def _linha_selecionada_id(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            return None
        item_id = self.tabela.item(linha, 0)
        return int(item_id.text()) if item_id else None

    def _ao_dar_duplo_clique(self, _indice):
        pessoa_id = self._linha_selecionada_id()
        if pessoa_id is not None:
            self.editar_solicitado.emit(pessoa_id)

    def _ao_clicar_editar(self):
        pessoa_id = self._linha_selecionada_id()
        if pessoa_id is not None:
            self.editar_solicitado.emit(pessoa_id)

    def _ao_clicar_excluir(self):
        pessoa_id = self._linha_selecionada_id()
        if pessoa_id is not None:
            self.excluir_solicitado.emit(pessoa_id)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def tem_selecao(self) -> bool:
        return self.tabela.currentRow() >= 0

    def carregar(self, registros) -> None:
        self.tabela.setRowCount(len(registros))
        for linha, registro in enumerate(registros):
            for coluna, valor in enumerate(registro):
                item = QTableWidgetItem(str(valor) if valor is not None else "")
                self.tabela.setItem(linha, coluna, item)
        self.tabela.resizeColumnsToContents()
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
