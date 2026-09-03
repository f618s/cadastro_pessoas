"""Widget responsável apenas pelos dados pessoais (nome, documento, e-mail, celular).

Isolar esse pedaço da tela em sua própria classe deixa o MainWindow mais
enxuto e permite testar/reaproveitar o formulário isoladamente.
"""

from PySide6.QtWidgets import QComboBox, QGridLayout, QGroupBox, QLabel, QLineEdit

from app.validators import formatar_celular, formatar_documento
from app.ui.widgets.base import limpar_erros, marcar_erro


class PersonalDataForm(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Dados pessoais", parent)
        self._montar_layout()

    def _montar_layout(self):
        layout = QGridLayout(self)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(10)

        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Digite o nome completo")

        self.tipo_documento = QComboBox()
        self.tipo_documento.addItems(["CPF", "CNPJ"])
        self.tipo_documento.currentTextChanged.connect(self._ao_trocar_tipo_documento)

        self.documento = QLineEdit()
        self.documento.setPlaceholderText("000.000.000-00")
        self.documento.textEdited.connect(self._ao_editar_documento)

        self.email = QLineEdit()
        self.email.setPlaceholderText("exemplo@email.com")

        self.celular = QLineEdit()
        self.celular.setPlaceholderText("(11) 99999-9999")
        self.celular.textEdited.connect(self._ao_editar_celular)

        layout.addWidget(self._rotulo("Nome completo *"), 0, 0)
        layout.addWidget(self.nome, 0, 1, 1, 3)

        layout.addWidget(self._rotulo("Documento *"), 1, 0)
        layout.addWidget(self.tipo_documento, 1, 1)
        layout.addWidget(self.documento, 1, 2, 1, 2)

        layout.addWidget(self._rotulo("E-mail *"), 2, 0)
        layout.addWidget(self.email, 2, 1, 1, 3)

        layout.addWidget(self._rotulo("Celular *"), 3, 0)
        layout.addWidget(self.celular, 3, 1, 1, 1)

    @staticmethod
    def _rotulo(texto):
        rotulo = QLabel(texto)
        rotulo.setObjectName("rotuloCampo")
        return rotulo

    # ------------------------------------------------------------------
    # Reações do usuário: máscara dinâmica
    # ------------------------------------------------------------------

    def _ao_trocar_tipo_documento(self, tipo):
        self.documento.clear()
        marcar_erro(self.documento, False)
        if tipo == "CPF":
            self.documento.setPlaceholderText("000.000.000-00")
        else:
            self.documento.setPlaceholderText("00.000.000/0000-00")

    def _ao_editar_documento(self, texto):
        formatado = formatar_documento(self.tipo_documento.currentText(), texto)
        self.documento.blockSignals(True)
        self.documento.setText(formatado)
        self.documento.blockSignals(False)

    def _ao_editar_celular(self, texto):
        formatado = formatar_celular(texto)
        self.celular.blockSignals(True)
        self.celular.setText(formatado)
        self.celular.blockSignals(False)

    # ------------------------------------------------------------------
    # API pública usada pela janela principal
    # ------------------------------------------------------------------

    def obter_dados(self) -> dict:
        return {
            "nome": self.nome.text().strip(),
            "tipo_documento": self.tipo_documento.currentText(),
            "documento": self.documento.text().strip(),
            "email": self.email.text().strip(),
            "celular": self.celular.text().strip(),
        }

    def preencher(self, pessoa) -> None:
        self.nome.setText(pessoa.nome)
        indice = self.tipo_documento.findText(pessoa.tipo_documento)
        self.tipo_documento.setCurrentIndex(max(indice, 0))
        self.documento.setText(formatar_documento(pessoa.tipo_documento, pessoa.documento))
        self.email.setText(pessoa.email)
        self.celular.setText(formatar_celular(pessoa.celular))

    def limpar(self) -> None:
        self.nome.clear()
        self.tipo_documento.setCurrentIndex(0)
        self.documento.clear()
        self.email.clear()
        self.celular.clear()
        limpar_erros(self.nome, self.documento, self.email, self.celular)

    def destacar_campos_invalidos(self, campos_invalidos: set) -> None:
        marcar_erro(self.nome, "nome" in campos_invalidos)
        marcar_erro(self.documento, "documento" in campos_invalidos)
        marcar_erro(self.email, "email" in campos_invalidos)
        marcar_erro(self.celular, "celular" in campos_invalidos)

    def possui_dados_preenchidos(self) -> bool:
        return any([
            self.nome.text().strip(),
            self.documento.text().strip(),
            self.email.text().strip(),
            self.celular.text().strip(),
        ])

    def focar_nome(self) -> None:
        self.nome.setFocus()
