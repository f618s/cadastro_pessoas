"""Ponto de entrada da aplicação de Cadastro de Pessoas.

Este arquivo cuida de três coisas antes de abrir a janela:

1. Configura logging em arquivo (app.log), para que problemas relatados
   pelo usuário possam ser investigados depois, mesmo sem reproduzir o
   erro ao vivo.
2. Instala um "gancho" global de exceções não tratadas (sys.excepthook).
   Se algo inesperado escapar de todos os try/except da aplicação, o
   usuário vê uma mensagem amigável em vez de a aplicação simplesmente
   fechar sem explicação.
3. Resolve o caminho do banco de dados de forma independente da pasta
   a partir da qual o programa foi executado.
"""

import logging
import sys
import traceback
from pathlib import Path

PASTA_APP = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA_APP))

from app.constants import NOME_BANCO  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(PASTA_APP / "app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("cadastro_pessoas")


def instalar_tratamento_global_de_erros(app):
    """Evita que uma exceção não prevista derrube a aplicação em silêncio."""
    from PySide6.QtWidgets import QMessageBox

    def tratador(tipo, valor, tb):
        if issubclass(tipo, KeyboardInterrupt):
            sys.__excepthook__(tipo, valor, tb)
            return

        texto_completo = "".join(traceback.format_exception(tipo, valor, tb))
        logger.critical("Exceção não tratada:\n%s", texto_completo)

        QMessageBox.critical(
            None,
            "Erro inesperado",
            "Ocorreu um erro inesperado e não previsto pela aplicação.\n\n"
            f"Detalhes: {valor}\n\n"
            f"Mais informações foram registradas em:\n{PASTA_APP / 'app.log'}",
        )

    sys.excepthook = tratador


def main():
    from PySide6.QtWidgets import QApplication, QMessageBox

    from app.services.database import Database
    from app.exceptions import BancoDadosError
    from app.ui.main_window import CadastroWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Cadastro de Pessoas")

    instalar_tratamento_global_de_erros(app)

    caminho_banco = PASTA_APP / NOME_BANCO

    try:
        database = Database(caminho_banco)
    except BancoDadosError as erro:
        logger.error("Falha ao inicializar o banco de dados: %s", erro)
        QMessageBox.critical(None, "Não foi possível iniciar", str(erro))
        sys.exit(1)

    janela = CadastroWindow(database)
    janela.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
