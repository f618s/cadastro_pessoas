"""Execução da consulta de CEP em uma thread separada.

A implementação original chamava requests.get(...) diretamente no método
do botão e usava QApplication.processEvents() para a janela não travar.
Isso funciona, mas é frágil: se o usuário clicar em outro botão durante
a consulta, ou fechar a janela, o comportamento fica imprevisível.

Rodar a consulta em uma QThread resolve isso de forma correta: a
interface continua responsiva, o botão pode ser desabilitado com
segurança durante a consulta, e é possível encerrar a aplicação sem
deixar a requisição "presa".
"""

from PySide6.QtCore import QThread, Signal

from app.exceptions import (
    CepConexaoError,
    CepInvalidoError,
    CepNaoEncontradoError,
    CepRespostaInvalidaError,
)
from app.services.viacep import consultar_cep


class CepWorker(QThread):
    sucesso = Signal(dict)
    falha = Signal(str, str)  # (categoria, mensagem)

    def __init__(self, cep: str, parent=None):
        super().__init__(parent)
        self._cep = cep

    def run(self):
        try:
            endereco = consultar_cep(self._cep)
        except CepInvalidoError as erro:
            self.falha.emit("invalido", str(erro))
        except CepNaoEncontradoError as erro:
            self.falha.emit("nao_encontrado", str(erro))
        except CepConexaoError as erro:
            self.falha.emit("conexao", str(erro))
        except CepRespostaInvalidaError as erro:
            self.falha.emit("resposta_invalida", str(erro))
        except Exception as erro:  # última linha de defesa: nunca travar a UI
            self.falha.emit("inesperado", f"Erro inesperado ao consultar o CEP: {erro}")
        else:
            self.sucesso.emit(endereco)
