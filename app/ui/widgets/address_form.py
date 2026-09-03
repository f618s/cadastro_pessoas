"""Widget responsável pelo endereço e pela consulta de CEP.

A consulta em si (chamada de rede) não acontece aqui: este widget apenas
emite o sinal `consulta_solicitada` com o CEP digitado. Quem decide como
consultar (via QThread) é o MainWindow, o que mantém este widget simples
e sem responsabilidade sobre concorrência/threads.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from app.constants import ESTADOS
from app.validators import formatar_cep
from app.ui.widgets.base import limpar_erros, marcar_erro


class AddressForm(QGroupBox):
    consulta_solicitada = Signal(str)

    def __init__(self, parent=None):
        super().__init__("Endereço", parent)
        self._montar_layout()

    def _montar_layout(self):
        layout = QGridLayout(self)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(10)

        self.cep = QLineEdit()
        self.cep.setPlaceholderText("00000-000")
        self.cep.setMaxLength(9)
        self.cep.textEdited.connect(self._ao_editar_cep)
        self.cep.returnPressed.connect(self._solicitar_consulta)

        self.btn_cep = QPushButton("Consultar CEP")
        self.btn_cep.setToolTip("Buscar automaticamente logradouro, bairro, cidade e estado")
        self.btn_cep.clicked.connect(self._solicitar_consulta)

        self.status_cep = QLabel("")
        self.status_cep.setObjectName("mensagemErroCampo")

        linha_cep = QHBoxLayout()
        linha_cep.addWidget(self.cep)
        linha_cep.addWidget(self.btn_cep)

        self.logradouro = QLineEdit()
        self.numero = QLineEdit()
        self.complemento = QLineEdit()
        self.complemento.setPlaceholderText("Apto, bloco, casa... (opcional)")
        self.bairro = QLineEdit()
        self.cidade = QLineEdit()

        self.estado = QComboBox()
        self.estado.addItem("Selecione...", "")
        for sigla, nome in ESTADOS:
            self.estado.addItem(f"{sigla} - {nome}", sigla)

        layout.addWidget(self._rotulo("CEP *"), 0, 0)
        layout.addLayout(linha_cep, 0, 1, 1, 3)
        layout.addWidget(self.status_cep, 1, 1, 1, 3)

        layout.addWidget(self._rotulo("Logradouro *"), 2, 0)
        layout.addWidget(self.logradouro, 2, 1, 1, 3)

        layout.addWidget(self._rotulo("Número *"), 3, 0)
        layout.addWidget(self.numero, 3, 1)

        layout.addWidget(self._rotulo("Complemento"), 3, 2)
        layout.addWidget(self.complemento, 3, 3)

        layout.addWidget(self._rotulo("Bairro *"), 4, 0)
        layout.addWidget(self.bairro, 4, 1)

        layout.addWidget(self._rotulo("Cidade *"), 4, 2)
        layout.addWidget(self.cidade, 4, 3)

        layout.addWidget(self._rotulo("Estado *"), 5, 0)
        layout.addWidget(self.estado, 5, 1)

    @staticmethod
    def _rotulo(texto):
        rotulo = QLabel(texto)
        rotulo.setObjectName("rotuloCampo")
        return rotulo

    def _ao_editar_cep(self, texto):
        formatado = formatar_cep(texto)
        self.cep.blockSignals(True)
        self.cep.setText(formatado)
        self.cep.blockSignals(False)
        self.status_cep.setText("")

    def _solicitar_consulta(self):
        self.consulta_solicitada.emit(self.cep.text().strip())

    # ------------------------------------------------------------------
    # Controle de estado visual durante a consulta assíncrona
    # ------------------------------------------------------------------

    def iniciar_consulta_visual(self):
        self.btn_cep.setEnabled(False)
        self.btn_cep.setText("Consultando...")
        self.cep.setEnabled(False)
        self.status_cep.setStyleSheet("color: #5b6b7b;")
        self.status_cep.setText("Consultando o endereço, aguarde...")

    def finalizar_consulta_visual(self, mensagem_erro: str | None = None):
        self.btn_cep.setEnabled(True)
        self.btn_cep.setText("Consultar CEP")
        self.cep.setEnabled(True)

        if mensagem_erro:
            self.status_cep.setStyleSheet("color: #c0392b;")
            self.status_cep.setText(mensagem_erro)
            marcar_erro(self.cep, True)
        else:
            self.status_cep.setStyleSheet("color: #2e7d32;")
            self.status_cep.setText("Endereço localizado com sucesso.")
            marcar_erro(self.cep, False)

    # ------------------------------------------------------------------
    # API pública usada pela janela principal
    # ------------------------------------------------------------------

    def preencher_endereco(self, endereco: dict) -> None:
        self.logradouro.setText(endereco.get("logradouro", ""))
        self.bairro.setText(endereco.get("bairro", ""))
        self.cidade.setText(endereco.get("cidade", ""))

        indice = self.estado.findData(endereco.get("estado", ""))
        if indice >= 0:
            self.estado.setCurrentIndex(indice)

    def obter_dados(self) -> dict:
        return {
            "cep": self.cep.text().strip(),
            "logradouro": self.logradouro.text().strip(),
            "numero": self.numero.text().strip(),
            "complemento": self.complemento.text().strip(),
            "bairro": self.bairro.text().strip(),
            "cidade": self.cidade.text().strip(),
            "estado": self.estado.currentData() or "",
        }

    def preencher(self, pessoa) -> None:
        self.cep.setText(formatar_cep(pessoa.cep))
        self.logradouro.setText(pessoa.logradouro)
        self.numero.setText(pessoa.numero)
        self.complemento.setText(pessoa.complemento)
        self.bairro.setText(pessoa.bairro)
        self.cidade.setText(pessoa.cidade)
        indice = self.estado.findData(pessoa.estado)
        self.estado.setCurrentIndex(max(indice, 0))

    def limpar(self) -> None:
        self.cep.clear()
        self.logradouro.clear()
        self.numero.clear()
        self.complemento.clear()
        self.bairro.clear()
        self.cidade.clear()
        self.estado.setCurrentIndex(0)
        self.status_cep.setText("")
        limpar_erros(
            self.cep, self.logradouro, self.numero, self.bairro,
            self.cidade, self.estado,
        )

    def destacar_campos_invalidos(self, campos_invalidos: set) -> None:
        marcar_erro(self.cep, "cep" in campos_invalidos)
        marcar_erro(self.logradouro, "logradouro" in campos_invalidos)
        marcar_erro(self.numero, "numero" in campos_invalidos)
        marcar_erro(self.bairro, "bairro" in campos_invalidos)
        marcar_erro(self.cidade, "cidade" in campos_invalidos)
        marcar_erro(self.estado, "estado" in campos_invalidos)

    def possui_dados_preenchidos(self) -> bool:
        return any([
            self.cep.text().strip(),
            self.logradouro.text().strip(),
            self.numero.text().strip(),
            self.bairro.text().strip(),
            self.cidade.text().strip(),
            self.estado.currentData(),
        ])
